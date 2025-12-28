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
    # Public endpoints
    path('register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # User endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Admin-only endpoints
    path('admin/create-shop-owner/', AdminCreateShopOwnerView.as_view(), name='create_shop_owner'),
]

# shops/urls.py


urlpatterns = [
    # Public endpoints
    path('shops/', ShopListView.as_view(), name='shop_list'),
    path('shops/nearby/', NearbyShopsView.as_view(), name='nearby_shops'),
    path('shops/<int:pk>/', ShopDetailView.as_view(), name='shop_detail'),
    
    # Shop owner endpoints
    path('my-shop/', ShopOwnerShopView.as_view(), name='my_shop'),
    
    # Admin endpoints
    path('admin/shops/create/', AdminShopCreateView.as_view(), name='admin_create_shop'),
    path('admin/shops/', AdminShopManagementView.as_view(), name='admin_shop_management'),
    path('admin/shops/<int:pk>/approve/', AdminApproveShopView.as_view(), name='admin_approve_shop'),
]
