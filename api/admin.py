from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

admin.site.site_header = "Laundry Management System"
admin.site.site_title = "Admin"
admin.site.index_title = "Dashboard"

@admin.register(User)
class CustomUserAdmin(UserAdmin):
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