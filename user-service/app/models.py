from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 1. Định nghĩa 3 vai trò chuẩn theo tiểu luận
    ROLE_CHOICES = (
        ('admin', 'Admin/Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )
    
    # 2. Trường phân quyền
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # 3. MANG TỪ MANAGER SANG: Khai báo thêm trường department (phòng ban)
    # Để blank=True, null=True vì chỉ có Admin/Manager mới cần trường này, Customer thì không
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"