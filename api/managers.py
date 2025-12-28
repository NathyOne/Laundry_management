# accounts/managers.py
from django.contrib.auth.models import BaseUserManager
from django.core.mail import send_mail
from django.conf import settings
import secrets

class CustomUserManager(BaseUserManager):
    """
    Custom manager with restricted shop owner creation
    """
    
    def create_user(self, email, password=None, user_type='customer', **extra_fields):
        """Create a regular user (customer by default)"""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        
        # Prevent non-admins from creating shop owners
        if user_type == 'shop_owner':
            raise ValueError('Only admins can create shop owner accounts')
        
        user = self.model(
            email=email,
            user_type=user_type,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        else:
            # Generate random password for admin-created users
            password = secrets.token_urlsafe(12)
            user.set_password(password)
        
        user.save(using=self._db)
        return user
    
    def create_customer(self, email, password=None, **extra_fields):
        """Public method for customer registration"""
        extra_fields.setdefault('user_type', 'customer')
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)
    
    def create_shop_owner(self, email, first_name, last_name, phone='', **extra_fields):
        """
        Admin-only method to create shop owner accounts
        Returns: (user, temp_password)
        """
        # Generate temporary password
        temp_password = secrets.token_urlsafe(12)
        
        user = self.model(
            email=self.normalize_email(email),
            user_type='shop_owner',
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_active=True,
            is_staff=False,  # Shop owners don't get admin access
            **extra_fields
        )
        user.set_password(temp_password)
        user.save(using=self._db)
        
        return user, temp_password
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create a superuser/admin"""
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)