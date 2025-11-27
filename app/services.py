from decimal import Decimal
from typing import Dict, List, Optional

from django.db import transaction
from django.db.models import F

from app.models import Category, CustomerProfile, Order, OrderItem, Product, SupplierProfile


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
        return product

    @staticmethod
    def list_products() -> List[Product]:
        return list(Product.objects.all())


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
        return order
