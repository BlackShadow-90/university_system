from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User, Role, Permission, RolePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'created_at']
    list_filter = ['role']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name_en', 'role', 'status', 'is_active', 'created_at']
    list_filter = ['role', 'status', 'is_active', 'created_at']
    search_fields = ['email', 'full_name_en', 'full_name_zh', 'phone']
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'last_login_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('uuid', 'full_name_en', 'full_name_zh', 'email', 'phone', 'avatar')
        }),
        (_('Role & Status'), {
            'fields': ('role', 'status', 'is_staff', 'is_active', 'is_superuser')
        }),
        (_('Timestamps'), {
            'fields': ('last_login_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
