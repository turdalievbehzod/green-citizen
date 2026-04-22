from django.contrib import admin

from apps.users.models.permissions import Role, Endpoint, Permission
from apps.users.models.user_permissions import UserPermission
from apps.users.models.users import User


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'parent', 'created_at']
    search_fields = ['name', 'codename']
    list_filter = ['parent']
    ordering = ['-id']


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ['path', 'method', 'name', 'permission', 'is_active']
    search_fields = ['path', 'name']
    list_filter = ['method', 'is_active', 'permission']
    list_editable = ['is_active']
    ordering = ['-path']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['permissions']
    list_filter = ['is_active']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'is_staff']
    search_fields = ['username', 'email']
    filter_horizontal = ['roles']


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'created_at']
    search_fields = ['id']
    list_filter = ['created_at']
    ordering = ['-id']