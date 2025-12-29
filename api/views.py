# from django.shortcuts import render

# from rest_framework.viewsets import ModelViewSet
# from .serializers import ShopSerializer, OwnerSerializer
# from .models import Shop, Owner

# # Create your views here.
# class LaundryShopViewSet(ModelViewSet):
#     serializer_class = ShopSerializer
#     queryset = Shop.objects.all()


# class OwnersViewset(ModelViewSet):
#     serializer_class = OwnerSerializer
#     queryset = Owner.objects.all()


# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    CustomerRegistrationSerializer,
    ShopOwnerCreateSerializer,
    UserSerializer
)
from .permissions import IsAdminUser
from rest_framework import generics, permissions, status, filters
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
import math
from .models import Shop
from .serializers import ShopSerializer, ShopCreateSerializer
from .permissions import IsAdminUser, IsShopOwner, IsOwnerOrAdmin

User = get_user_model()

class CustomerRegisterView(generics.CreateAPIView):
    """Customer self-registration (public)"""
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        # Send welcome email
        send_mail(
            subject='Welcome to Laundry Service!',
            message=f'Hi {user.first_name},\n\nWelcome to our laundry service app!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Customer registered successfully'
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """Login view for all user types"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, email=email, password=password)
        
        if user:
            if not user.is_active:
                return Response(
                    {'error': 'Account is deactivated'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'user_type': user.user_type,
                'message': 'Login successful'
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

class AdminCreateShopOwnerView(generics.CreateAPIView):
    """Admin creates shop owner accounts"""
    serializer_class = ShopOwnerCreateSerializer
    permission_classes = [IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create shop owner with temporary password
        user, temp_password = User.objects.create_shop_owner(**serializer.validated_data)
        
        # Send credentials email
        send_mail(
            subject='Your Laundry Shop Owner Account',
            message=f"""
            Hi {user.first_name},
            
            An admin has created a shop owner account for you.
            
            Login Details:
            Email: {user.email}
            Temporary Password: {temp_password}
            
            Please login and change your password immediately.
            
            Regards,
            Laundry Service Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Shop owner created successfully. Credentials sent via email.',
            'temporary_password': temp_password  # Only shown to admin in response
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get/update user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    



###################################################################################################


class ShopListView(generics.ListAPIView):
    """List all active shops (public)"""
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'region', 'address']
    ordering_fields = ['average_rating', 'base_wash_price', 'created_at']
    
    def get_queryset(self):
        queryset = Shop.objects.filter(status='active')
        
        # Filter by city if provided
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        # Filter by region if provided
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(region__iexact=region)
        
        # Filter by delivery availability
        delivery = self.request.query_params.get('delivery')
        if delivery:
            queryset = queryset.filter(delivery_available=True)
        
        return queryset
    
    def get_serializer_context(self):
        """Pass request context to serializer for distance calculation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class NearbyShopsView(generics.ListAPIView):
    """Find nearby shops based on coordinates"""
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_lat = self.request.query_params.get('lat')
        user_lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)  # Default 10km
        
        if not user_lat or not user_lng:
            return Shop.objects.none()
        
        try:
            user_lat = float(user_lat)
            user_lng = float(user_lng)
            radius = float(radius)
            
            # Get all active shops
            shops = Shop.objects.filter(status='active')
            
            # Calculate distance for each shop
            nearby_shops = []
            for shop in shops:
                if shop.latitude and shop.longitude:
                    distance = self.calculate_distance(
                        user_lat, user_lng,
                        float(shop.latitude), float(shop.longitude)
                    )
                    if distance <= radius:
                        shop.distance = distance
                        nearby_shops.append(shop)
            
            # Sort by distance
            nearby_shops.sort(key=lambda x: x.distance)
            return nearby_shops
            
        except (ValueError, TypeError):
            return Shop.objects.none()
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Haversine formula for distance calculation"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

class ShopDetailView(generics.RetrieveAPIView):
    """Get shop details (public)"""
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Shop.objects.filter(status='active')

class AdminShopCreateView(generics.CreateAPIView):
    """Admin creates a shop for a shop owner"""
    serializer_class = ShopCreateSerializer
    permission_classes = [IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shop = serializer.save()
        
        # Activate the shop
        shop.status = 'active'
        shop.save()
        
        return Response(
            ShopSerializer(shop).data,
            status=status.HTTP_201_CREATED
        )

class ShopOwnerShopView(generics.ListAPIView):
    """Shop owner lists their own shops"""
    serializer_class = ShopSerializer
    permission_classes = [IsShopOwner]

    def get_queryset(self):
        return Shop.objects.filter(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AdminShopManagementView(generics.ListAPIView):
    """Admin views all shops (including pending)"""
    serializer_class = ShopSerializer
    permission_classes = [IsAdminUser]
    queryset = Shop.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

class AdminApproveShopView(APIView):
    """Admin approves a pending shop"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk, status='pending')
            shop.status = 'active'
            shop.approved_at = timezone.now()
            shop.save()
            
            # Notify shop owner
            send_mail(
                subject='Your Shop Has Been Approved!',
                message=f"Hi {shop.owner.first_name},\n\nYour shop '{shop.name}' has been approved and is now active.\n\nRegards,\nAdmin Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[shop.owner.email],
                fail_silently=True,
            )
            
            return Response(
                {'message': 'Shop approved successfully'},
                status=status.HTTP_200_OK
            )
        except Shop.DoesNotExist:
            return Response(
                {'error': 'Shop not found or not pending'},
                status=status.HTTP_404_NOT_FOUND
            )