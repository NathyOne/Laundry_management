# from django.urls import path
# from rest_framework.routers import DefaultRouter
# from .views import LaundryShopViewSet, OwnersViewset

# router = DefaultRouter()

# router.register('laundries', LaundryShopViewSet)
# router.register('owners', OwnersViewset)

# urlpatterns = router.urls

# accounts/urls.py
from django.urls import path
from .views import (
    CustomerRegisterView,
    LoginView,
    AdminCreateShopOwnerView,
    UserProfileView
)
from django.urls import path
from .views import (
    ShopListView,
    NearbyShopsView,
    ShopDetailView,
    AdminShopCreateView,
    ShopOwnerShopView,
    AdminShopManagementView,
    AdminApproveShopView
)


urlpatterns = [
    path('register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # User endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Admin-only endpoints (use `admin-api/` to avoid colliding with Django admin)
    path('admin-api/create-shop-owner/', AdminCreateShopOwnerView.as_view(), name='create_shop_owner'),
    # Public endpoints
    path('shops/', ShopListView.as_view(), name='shop_list'),
    path('shops/nearby/', NearbyShopsView.as_view(), name='nearby_shops'),
    path('shops/<int:pk>/', ShopDetailView.as_view(), name='shop_detail'),
    
    # Shop owner endpoints
    path('my-shop/', ShopOwnerShopView.as_view(), name='my_shop'),
    
    # Admin endpoints (use `admin-api/` to avoid colliding with Django admin)
    path('admin-api/shops/create/', AdminShopCreateView.as_view(), name='admin_create_shop'),
    path('admin-api/shops/', AdminShopManagementView.as_view(), name='admin_shop_management'),
    path('admin-api/shops/<int:pk>/approve/', AdminApproveShopView.as_view(), name='admin_approve_shop'),
]
