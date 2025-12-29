from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

# Create your models here.

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # role/type of user: customer, shop_owner, admin
    USER_TYPES = (
        ('customer', 'Customer'),
        ('shop_owner', 'Shop Owner'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    email = models.EmailField(
        unique=True,  
        max_length=254,
        db_index=True
    )

    #status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def has_perm(self, perm, obj=None):
        """Return True if user has a specific permission.

        Keep this simple: grant permissions to staff or superusers.
        """
        return self.is_active and (self.is_superuser or self.is_staff)

    def has_module_perms(self, app_label):
        """Return True if user has permissions for the given app label."""
        return self.is_active and (self.is_superuser or self.is_staff)

    @property
    def is_admin(self):
        """Convenience property used across the codebase/permissions."""
        return self.is_active and (self.user_type == 'admin' or self.is_superuser)

    @property
    def is_shop_owner(self):
        return self.is_active and self.user_type == 'shop_owner'

    @property
    def is_customer(self):
        return self.is_active and self.user_type == 'customer'



class Shop(models.Model):
    """Laundry Shop Model"""
    SHOP_STATUS = (
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    )
    
    # Shop Info
    name = models.CharField(_('shop name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=SHOP_STATUS,
        default='pending'
    )
    
    # Shop Owner (created by admin)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop',
        limit_choices_to={'user_type': 'shop_owner'}
    )
    
    # Contact Information
    email = models.EmailField(_('shop email'), max_length=254)
    phone = models.CharField(_('shop phone'), max_length=20)
    
    # Address & Location
    address = models.TextField(_('full address'))
    city = models.CharField(_('city'), max_length=100, default='Addis Ababa')
    region = models.CharField(_('region'), max_length=100, default='Addis Ababa')
    country = models.CharField(_('country'), max_length=100, default='Ethiopia')
    
    # Coordinates for distance calculation
    latitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16,
        null=True,
        blank=True
    )
    
    # Shop Details
    opening_hours = models.CharField(_('opening hours'), max_length=200, default='9:00 AM - 8:00 PM')
    delivery_available = models.BooleanField(_('delivery available'), default=False)
    pickup_available = models.BooleanField(_('pickup available'), default=True)
    
    # Ratings
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Images
    logo = models.ImageField(
        _('shop logo'),
        upload_to='shop_logos/',
        blank=True,
        null=True
    )
    banner_image = models.ImageField(
        ('banner image'),
        upload_to='shop_banners/',
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('laundry shop')
        verbose_name_plural = _('laundry shops')
        indexes = [
            models.Index(fields=['city', 'status']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def full_location(self):
        return f"{self.address}, {self.city}, {self.region}, {self.country}"


class Cloth_type(models.Model):
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


