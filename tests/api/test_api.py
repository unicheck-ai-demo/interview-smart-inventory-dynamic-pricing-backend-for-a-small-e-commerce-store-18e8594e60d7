import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from app.models import Category, CustomerProfile, Product, SupplierProfile

pytestmark = pytest.mark.django_db


def test_product_list_api(api_client):
    cat = Category.objects.create(name='Bowls')
    supp = SupplierProfile.objects.create(name='CeramicWorld')
    Product.objects.create(name='Porcelain Bowl', category=cat, supplier=supp, price=11.0, stock_quantity=20)
    url = reverse('api:product-list')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()['results'][0]['name'] == 'Porcelain Bowl'


def test_order_place_api(authenticated_api_client):
    cat = Category.objects.create(name='Cups')
    supp = SupplierProfile.objects.create(name='CupMaker')
    prod = Product.objects.create(name='Teacup', category=cat, supplier=supp, price=8.5, stock_quantity=10)
    user = User.objects.get(username='testuser')
    prof = CustomerProfile.objects.create(user=user)
    url = reverse('api:order-list')
    data = {'items': [{'product_id': prod.id, 'quantity': 3}]}
    resp = authenticated_api_client.post(url, data, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    prod.refresh_from_db()
    assert prod.stock_quantity == 7


def test_dynamic_pricing(authenticated_api_client):
    cat = Category.objects.create(name='Saucepans')
    supp = SupplierProfile.objects.create(name='Panworks')
    prod = Product.objects.create(
        name='Small Pan', category=cat, supplier=supp, price=30.0, stock_quantity=1, restock_threshold=2
    )
    user = User.objects.get(username='testuser')
    CustomerProfile.objects.create(user=user)
    url = reverse('api:product-dynamic-pricing', args=[prod.id])
    resp = authenticated_api_client.post(url, {'demand': 10}, format='json')
    assert resp.status_code == status.HTTP_200_OK
    assert float(resp.json()['new_price']) > 30.0


def test_analytics_endpoint(authenticated_api_client):
    cat = Category.objects.create(name='AnalyticsCat')
    supp = SupplierProfile.objects.create(name='AnSupp')
    product = Product.objects.create(name='ItemAnalytics', category=cat, supplier=supp, price=10, stock_quantity=19)
    user = User.objects.get(username='testuser')
    prof = CustomerProfile.objects.create(user=user)
    from app.services import OrderService

    OrderService.place_order(prof, items=[{'product_id': product.id, 'quantity': 2}])
    url = reverse('api:analytics')
    resp = authenticated_api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    report = resp.json()
    assert any(row['name'] == 'ItemAnalytics' for row in report)
