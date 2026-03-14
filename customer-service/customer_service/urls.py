from django.contrib import admin
from django.urls import path
from app.views import CustomerListCreate

urlpatterns = [
    path('admin/', admin.site.urls),
    # Định tuyến đường dẫn /customers/ vào class View ta vừa tạo
    path('customers/', CustomerListCreate.as_view(), name='customer-api'),
]