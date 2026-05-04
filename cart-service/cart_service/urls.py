"""
URL configuration for cart_service project.

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

from django.contrib import admin
from django.urls import path
from app.views import CartListView, AddToCartView, RemoveFromCartView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Các API của Giỏ hàng

    path('api/cart/', CartListView.as_view(), name='cart-list'),
    path('api/cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('api/cart/remove/', RemoveFromCartView.as_view(), name='cart-remove'),
]