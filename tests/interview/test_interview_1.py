from decimal import Decimal

import pytest

from app.models import Category, Product, SupplierProfile
from app.services import ProductService

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(strict=True)
def test_currency_conversion_calculation_error():
    cat = Category.objects.create(name='InterviewCat')
    supp = SupplierProfile.objects.create(name='InterviewSupp')
    prod = Product.objects.create(
        name='InterviewProduct', category=cat, supplier=supp, price=Decimal('10.00'), stock_quantity=1
    )
    ProductService.update_multi_currency_prices(prod, {'EUR': Decimal('0.5')})
    prod.refresh_from_db()
    assert prod.prices_multi_currency.get('EUR') == '5.00'
