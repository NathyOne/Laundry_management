from rest_framework import serializers
from .models import Shop
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
import math

User = get_user_model()

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer self-registration"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_customer(**validated_data)

class ShopOwnerCreateSerializer(serializers.ModelSerializer):
    """Admin-only serializer for creating shop owners"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def create(self, validated_data):
        # This will be handled in the view
        return validated_data

class UserSerializer(serializers.ModelSerializer):
    """User details serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'first_name', 'last_name', 
                 'phone', 'is_active', 'date_joined']
        read_only_fields = ['user_type', 'is_active', 'date_joined']






# class ShopSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = Shop
#         fields = '__all__'




User = get_user_model()

class ShopSerializer(serializers.ModelSerializer):
    """Shop serializer for listing/details"""
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'description', 'status', 'owner_name', 'owner_email',
            'email', 'phone', 'address', 'city', 'region', 'country',
            'latitude', 'longitude', 'opening_hours', 'delivery_available',
            'pickup_available', 'average_rating',
            'total_reviews', 'logo', 'banner_image', 'distance',
            'created_at', 'is_active'
        ]
        read_only_fields = ['average_rating', 'total_reviews', 'created_at']
    
    def get_owner_name(self, obj):
        return obj.owner.email if obj.owner else ''
    
    def get_distance(self, obj):
        """Calculate distance if user coordinates provided"""
        request = self.context.get('request')
        if request:
            user_lat = request.query_params.get('user_lat')
            user_lng = request.query_params.get('user_lng')
            
            if user_lat and user_lng and obj.latitude and obj.longitude:
                try:
                    return self.calculate_distance(
                        float(user_lat), float(user_lng),
                        float(obj.latitude), float(obj.longitude)
                    )
                except (ValueError, TypeError):
                    pass
        return None
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in km"""
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return round(R * c, 2)  # Distance in km

class ShopCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating shops (admin/shop owner only)"""
    owner_email = serializers.EmailField(write_only=True, required=True)
    
    class Meta:
        model = Shop
        fields = [
            'name', 'description', 'owner_email',
            'email', 'phone', 'address', 'city', 'region', 'country',
            'latitude', 'longitude', 'opening_hours', 'delivery_available',
            'pickup_available', 'logo', 'banner_image'
        ]
    
    def validate_owner_email(self, value):
        """Check if owner exists and is a shop owner"""
        try:
            owner = User.objects.get(email=value, user_type='shop_owner')
        except User.DoesNotExist:
            raise serializers.ValidationError("No shop owner found with this email")
        
        # Check if shop owner already has a shop
        # if hasattr(owner, 'shop'):
        #     raise serializers.ValidationError("This shop owner already has a shop")
        
        return value
    
    def create(self, validated_data):
        owner_email = validated_data.pop('owner_email')
        owner = User.objects.get(email=owner_email, user_type='shop_owner')
        
        shop = Shop.objects.create(owner=owner, **validated_data)
        return shop
