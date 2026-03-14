from django.contrib import admin
from django.urls import path
from app.views import RecommendBooks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ai/recommend/<int:customer_id>/', RecommendBooks.as_view(), name='ai-recommend'),
]