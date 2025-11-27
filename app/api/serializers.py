from django.contrib.auth.models import User
from rest_framework import serializers

from app.models import Category, CustomerProfile, Order, OrderItem, Product, SupplierProfile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class SupplierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProfile
        fields = ['id', 'name', 'contact_name', 'email', 'phone', 'location', 'address', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category',
            'tags',
            'supplier',
            'description',
            'stock_quantity',
            'restock_threshold',
            'price',
            'prices_multi_currency',
            'is_active',
            'created_at',
            'updated_at',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'address', 'phone', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerProfileSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'total', 'created_at', 'updated_at', 'items']
