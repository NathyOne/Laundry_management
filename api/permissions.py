# accounts/permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Only allow admin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsShopOwner(permissions.BasePermission):
    """Only allow shop owners"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_shop_owner

class IsCustomer(permissions.BasePermission):
    """Only allow customers"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer

class IsShopOwnerOrReadOnly(permissions.BasePermission):
    """Allow shop owners to edit, others to read"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow owners or admins"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return request.user.is_admin or obj.owner == request.user
        return request.user.is_admin or obj == request.user