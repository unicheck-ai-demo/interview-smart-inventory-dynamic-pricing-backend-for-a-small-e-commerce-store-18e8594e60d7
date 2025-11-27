from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class SupplierProfile(models.Model):
    name = models.CharField(max_length=128, unique=True)
    contact_name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    address = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT)
    tags = models.JSONField(default=list, blank=True)  # list of strings
    supplier = models.ForeignKey(SupplierProfile, related_name='products', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    restock_threshold = models.PositiveIntegerField(default=10)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    prices_multi_currency = JSONField(default=dict)  # e.g., {"USD": 12.40, "EUR": 11.50}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'category', 'supplier')

    def __str__(self):
        return self.name


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, related_name='customer_profile', on_delete=models.CASCADE)
    address = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    customer = models.ForeignKey(CustomerProfile, related_name='orders', on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} for {self.customer.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
