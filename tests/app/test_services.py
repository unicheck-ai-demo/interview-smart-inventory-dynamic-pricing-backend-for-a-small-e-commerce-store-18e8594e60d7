from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from app.services import CategoryService, CustomerProfileService, OrderService, ProductService, SupplierService

pytestmark = pytest.mark.django_db


def test_category_product_crud():
    c = CategoryService.create_category('Knives', 'Sharp tools')
    s = SupplierService.create_supplier('BladeMaker')
    p = ProductService.create_product('Santoku Knife', c, s, Decimal('45.00'), stock_quantity=5)
    assert p.name == 'Santoku Knife'
    fetched = ProductService.get_product(p.id)
    assert fetched == p
    products = ProductService.list_products()
    assert p in products


def test_simple_order_and_stock():
    c = CategoryService.create_category('Boards')
    s = SupplierService.create_supplier('WoodArt')
    prod = ProductService.create_product('Cutting Board', c, s, Decimal('29.99'), stock_quantity=5)
    user = User.objects.create(username='c1')
    prof = CustomerProfileService.create_profile(user, 'Addr', '555-1')
    order = OrderService.place_order(prof, items=[{'product_id': prod.id, 'quantity': 2}])
    prod.refresh_from_db()
    assert prod.stock_quantity == 3
    assert order.items.count() == 1
