from django.contrib import admin
from django.apps import apps

# Lấy tất cả các class đã được định nghĩa trong file models.py
models = apps.get_models()

# Tự động duyệt qua và đăng ký toàn bộ lên trang Admin
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        # Bỏ qua nếu model đó đã được đăng ký rồi
        pass