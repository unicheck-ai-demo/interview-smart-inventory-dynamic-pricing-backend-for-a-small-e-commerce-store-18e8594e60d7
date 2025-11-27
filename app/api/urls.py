from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsView,
    CategoryViewSet,
    CustomerProfileViewSet,
    HealthCheckView,
    OrderViewSet,
    ProductViewSet,
    SupplierProfileViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'suppliers', SupplierProfileViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerProfileViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]

app_name = 'api'
