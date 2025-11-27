from django.db import DatabaseError, connection
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Category, CustomerProfile, Order, Product, SupplierProfile
from app.services import (
    AnalyticsService,
    CurrencyService,
    CustomerProfileService,
    OrderService,
    ProductService,
)

from .serializers import (
    CategorySerializer,
    CustomerProfileSerializer,
    OrderSerializer,
    ProductSerializer,
    SupplierProfileSerializer,
)


class HealthCheckView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT PostGIS_Full_Version();')
                cursor.fetchone()
        except DatabaseError as e:
            return Response({'status': 'error', 'db': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SupplierProfileViewSet(viewsets.ModelViewSet):
    queryset = SupplierProfile.objects.all()
    serializer_class = SupplierProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], url_path='dynamic-pricing')
    def dynamic_pricing(self, request, pk=None):
        product = self.get_object()
        demand = int(request.data.get('demand', 0))
        try:
            new_price = ProductService.dynamic_pricing(product, demand)
            serializer = self.get_serializer(product)
            return Response({'new_price': str(new_price), 'product': serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-currency-prices')
    def update_currency_prices(self, request, pk=None):
        product = self.get_object()
        symbols = request.data.get('currencies', ['EUR', 'GBP'])
        try:
            rates = CurrencyService.fetch_rates_cached('USD', symbols)
            ProductService.update_multi_currency_prices(product, rates)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomerProfile.objects.select_related('user').all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related('items').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        profile = CustomerProfileService.get_profile_by_user(request.user)
        if not profile:
            return Response({'error': 'No customer profile.'}, status=status.HTTP_400_BAD_REQUEST)
        items = request.data.get('items', [])
        try:
            order = OrderService.place_order(profile, items=items)
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        try:
            OrderService.cancel_order(int(pk))
            return Response({'status': 'canceled'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        data = AnalyticsService.stock_and_sales_report()
        return Response(data)
