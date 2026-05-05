from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. Các cột hiển thị ngoài danh sách (Thêm cột role)
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    
    # 2. Bộ lọc bên phải màn hình (Lọc theo role)
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    # 3. Giao diện Cập nhật User (Thêm trường role vào nhóm tùy chỉnh)
    fieldsets = UserAdmin.fieldsets + (
        ('Phân quyền Microservices', {'fields': ('role',)}),
    )
    
    # 4. Giao diện Tạo mới User (Thêm trường role khi add user)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Phân quyền Microservices', {'fields': ('role',)}),
    )