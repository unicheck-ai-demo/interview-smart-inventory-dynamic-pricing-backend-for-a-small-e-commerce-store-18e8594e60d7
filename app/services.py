from decimal import Decimal
from typing import Dict, List, Optional

import redis
import requests
from django.conf import settings
from django.db import connection, transaction
from django.db.models import F

from app.models import Category, CustomerProfile, Order, OrderItem, Product, SupplierProfile


# Redis connection utility (for local simplicity, direct conn here)
def get_redis():
    return redis.StrictRedis.from_url(settings.CACHES['default']['LOCATION'])


class CategoryService:
    @staticmethod
    def create_category(name: str, description: str = '') -> Category:
        return Category.objects.create(name=name, description=description)

    @staticmethod
    def get_category_by_name(name: str) -> Optional[Category]:
        return Category.objects.filter(name=name).first()


class SupplierService:
    @staticmethod
    def create_supplier(name: str, **kwargs) -> SupplierProfile:
        return SupplierProfile.objects.create(name=name, **kwargs)

    @staticmethod
    def get_by_name(name: str) -> Optional[SupplierProfile]:
        return SupplierProfile.objects.filter(name=name).first()


class ProductService:
    @staticmethod
    def create_product(
        name: str, category: Category, supplier: SupplierProfile, price: Decimal, stock_quantity: int = 0, **kwargs
    ) -> Product:
        return Product.objects.create(
            name=name, category=category, supplier=supplier, price=price, stock_quantity=stock_quantity, **kwargs
        )

    @staticmethod
    def get_product(pk: int) -> Optional[Product]:
        return Product.objects.filter(pk=pk).first()

    @staticmethod
    def update_stock(product: Product, delta: int) -> Product:
        product.stock_quantity = F('stock_quantity') + delta
        product.save(update_fields=['stock_quantity'])
        product.refresh_from_db()
        # Inventory alert and redis cache
        if product.stock_quantity <= product.restock_threshold:
            redis_conn = get_redis()
            redis_conn.set(f'inventory_alert:{product.pk}', f'Low stock for {product.name}')
        return product

    @staticmethod
    def list_products_cached() -> List[Product]:
        redis_conn = get_redis()
        key = 'products:list'
        result = redis_conn.get(key)
        if result:
            ids = [int(pk) for pk in result.decode().split(',') if pk]
            return list(Product.objects.filter(pk__in=ids))
        products = Product.objects.all()
        ids = ','.join(str(p.pk) for p in products)
        redis_conn.set(key, ids, ex=120)
        return list(products)

    @staticmethod
    def list_products() -> List[Product]:
        return ProductService.list_products_cached()

    @staticmethod
    def invalidate_product_cache():
        get_redis().delete('products:list')

    @staticmethod
    def dynamic_pricing(product: Product, demand: int, concurrency_aware: bool = True) -> Decimal:
        # Multi-step transaction with savepoint. Rollback on demand error
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                # Simulate demand-based adjustment
                base_price = product.price
                adjustment = Decimal('0.00')
                if demand > product.stock_quantity:
                    adjustment += Decimal('5.00')  # Add premium if high demand
                elif product.stock_quantity < product.restock_threshold:
                    adjustment += Decimal('2.00')  # Add small premium for low stock
                new_price = base_price + adjustment
                product.price = new_price
                product.save(update_fields=['price'])
                transaction.savepoint_commit(sid)
                return new_price
            except Exception:
                transaction.savepoint_rollback(sid)
                raise

    @staticmethod
    def update_multi_currency_prices(product: Product, rates: Dict[str, Decimal]) -> None:
        base_usd = product.price
        product.prices_multi_currency = {c: str(base_usd + r) for c, r in rates.items()}
        product.save(update_fields=['prices_multi_currency'])
        get_redis().delete(f'currency_rates:{product.pk}')


class CurrencyService:
    @staticmethod
    def fetch_rates_cached(base: str = 'USD', symbols: List[str] = None) -> Dict[str, Decimal]:
        redis_conn = get_redis()
        key = f'currency_rates:{base}:' + ','.join(symbols or [])
        cached = redis_conn.get(key)
        if cached:
            import json

            return json.loads(cached.decode())
        # Simulated external call (replace URL for real provider)
        url = 'https://api.exchangerate.host/latest'
        params = {'base': base, 'symbols': ','.join(symbols or ['EUR', 'GBP'])}
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            rates = resp.json().get('rates', {})
            redis_conn.set(key, str(rates), ex=600)
            return rates
        raise Exception('Unable to fetch rates')


class CustomerProfileService:
    @staticmethod
    def create_profile(user, address: str = '', phone: str = '') -> CustomerProfile:
        return CustomerProfile.objects.create(user=user, address=address, phone=phone)

    @staticmethod
    def get_profile_by_user(user) -> Optional[CustomerProfile]:
        return CustomerProfile.objects.filter(user=user).first()


class OrderService:
    @staticmethod
    @transaction.atomic
    def place_order(customer_profile: CustomerProfile, items: List[Dict]) -> Order:
        order = Order.objects.create(customer=customer_profile, status='pending', total=Decimal('0.00'))
        total = Decimal('0.00')
        for item in items:
            product = Product.objects.select_for_update().get(pk=item['product_id'])
            if product.stock_quantity < item['quantity']:
                raise ValueError('Not enough stock for product: %s' % product.name)
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'], unit_price=product.price)
            ProductService.update_stock(product, -item['quantity'])
            total += product.price * item['quantity']
        order.total = total
        order.save(update_fields=['total'])
        ProductService.invalidate_product_cache()
        return order

    @staticmethod
    def cancel_order(order_id: int) -> None:
        order = Order.objects.get(id=order_id)
        for oi in order.items.all():
            ProductService.update_stock(oi.product, oi.quantity)
        order.status = 'canceled'
        order.save(update_fields=['status'])
        ProductService.invalidate_product_cache()


class AnalyticsService:
    @staticmethod
    def stock_and_sales_report() -> List[Dict]:
        # Raw SQL: join product/orderitem/order/customer
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.name, SUM(oi.quantity) AS sold, p.stock_quantity
                FROM app_product p
                LEFT JOIN app_orderitem oi ON oi.product_id = p.id
                GROUP BY p.id, p.name, p.stock_quantity
                ORDER BY sold DESC NULLS LAST, p.stock_quantity ASC
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
