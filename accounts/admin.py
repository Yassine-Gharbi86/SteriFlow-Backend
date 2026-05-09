from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email', 'full_name', 'role', 'is_active', 'created_at')
    list_filter   = ('role', 'is_active')
    search_fields = ('email', 'full_name')
    ordering      = ('-created_at',)

    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal',     {'fields': ('full_name',)}),
        ('Role & Access',{'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Audit',        {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
