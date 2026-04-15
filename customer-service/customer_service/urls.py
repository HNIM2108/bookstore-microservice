from django.contrib import admin
from django.urls import path
from app.views import CustomerListCreate
from app import views
from app.views import recommend_similar_books

urlpatterns = [
    path('admin/', admin.site.urls),
    # Định tuyến đường dẫn /customers/ vào class View ta vừa tạo
    path('customers/', CustomerListCreate.as_view(), name='customer-api'),
    path('customers/track/', views.track_behavior, name='track_behavior'),
    path('customers/<int:customer_id>/behavior/', views.get_behavior_history, name='get_behavior_history'),
    path('api/recommend/<int:book_id>/', recommend_similar_books),
]