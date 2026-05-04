from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Thêm hiển thị role và department vào trang Admin
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin phân quyền (RBAC)', {'fields': ('role', 'department')}),
    )
    list_display = ['username', 'email', 'role', 'department', 'is_staff']

admin.site.register(User, CustomUserAdmin)