from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.html import format_html
from .models import User, Shop

admin.site.site_header = "Laundry Management System"
admin.site.site_title = "Admin"
admin.site.index_title = "Dashboard"


class CustomUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes a read-only password hash display."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'phone', 'password',
            'is_active', 'is_staff', 'is_superuser', 'user_type', 'status'
        )

    def clean_password(self):
        return self.initial.get('password')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Fields to display in list view
    list_display = ['email', 'user_type', 'status', 'date_joined', 'is_active']
    
    # Filters for sidebar
    list_filter = ['user_type', 'status', 'is_superuser']
    
    # Search functionality
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    
    # Ordering
    ordering = ['-date_joined']
    
    # Fields in edit view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('user_type', 'status', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields shown when creating a new user in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    # Fields that can't be edited
    readonly_fields = ['date_joined', 'last_login']

    # Custom user model doesn't have group/user_permissions fields
    # Prevent UserAdmin default from referencing them
    filter_horizontal = ()
    
    # Add action buttons
    actions = ['make_active', 'make_inactive', 'make_suspended']
    
    # Custom actions
    def make_active(self, request, queryset):
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    make_active.short_description = "Mark selected users as Active"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(status='inactive', is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    make_inactive.short_description = "Mark selected users as Inactive"
    
    def make_suspended(self, request, queryset):
        updated = queryset.update(status='suspended', is_active=False)
        self.message_user(request, f'{updated} user(s) suspended successfully.')
    make_suspended.short_description = "Mark selected users as Suspended"


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'owner', 'email', 'address']
    actions = ['make_active', 'suspend', 'pending']

    def make_active(self, request, queryset):
        update = queryset.update(status = 'active')
        self.message_user(request, f'{update} Shop Activated!')
    make_active.short_description = "mark selected shop (s) Active!"
