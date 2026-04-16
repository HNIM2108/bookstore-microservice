from django.contrib import admin
from django.urls import path
from app.views import RecommendBooks, recommend_similar_books
from app.views import RecommendBooks, recommend_similar_books

urlpatterns = [
    path('admin/', admin.site.urls),
    # ĐÂY LÀ DÒNG QUAN TRỌNG NHẤT: Khớp với Frontend và trỏ vào hàm AI thật
    path('api/recommend/<int:book_id>/', recommend_similar_books),
    
    # Đường dẫn cũ giữ lại cho an toàn
    path('ai/recommend/<int:customer_id>/', RecommendBooks.as_view(), name='ai-recommend'),
]