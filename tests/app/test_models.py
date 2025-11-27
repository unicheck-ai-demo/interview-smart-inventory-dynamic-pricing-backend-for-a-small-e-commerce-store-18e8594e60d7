from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

from app.models import Category, CustomerProfile, Order, OrderItem, Product, SupplierProfile

pytestmark = pytest.mark.django_db


def test_create_category_and_supplier():
    cat = Category.objects.create(name='Cookware', description='Artisan pans')
    supp = SupplierProfile.objects.create(
        name='Artisan Co',
        contact_name='Ana',
        email='ana@example.com',
        location=Point(12.1, 50.3),
        address='123 Main St',
    )
    assert cat.pk is not None
    assert supp.pk is not None


def test_product_and_order_flow():
    cat = Category.objects.create(name='Utensils')
    supp = SupplierProfile.objects.create(name='Supp1')
    prod = Product.objects.create(
        name='Spatula', category=cat, supplier=supp, price=Decimal('9.25'), stock_quantity=100
    )
    user = User.objects.create_user('cust', 'e@example.com', 'pw')
    prof = CustomerProfile.objects.create(user=user, address='Addr 1')
    order = Order.objects.create(customer=prof, total=Decimal('18.50'))
    oi = OrderItem.objects.create(order=order, product=prod, quantity=2, unit_price=prod.price)
    assert order.items.count() == 1
    assert oi.product == prod
