"""
URL configuration for auth_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Đường dẫn để đăng nhập và lấy Token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 2. Đường dẫn để làm mới Token khi bị hết hạn
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 3. Đường dẫn MỚI để API Gateway xác thực thẻ (Verify)
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
