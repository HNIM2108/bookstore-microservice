from django.contrib import admin
from django.urls import path
from app.views import chat_with_bot, recommend_similar_books
from app.views import recommend_similar_books, graph_recommendations

urlpatterns = [
    path('admin/', admin.site.urls),
    # ĐÂY LÀ DÒNG QUAN TRỌNG NHẤT: Khớp với Frontend và trỏ vào hàm AI thật
    path('api/recommend/<int:book_id>/', recommend_similar_books),
    path('api/graph-recommend/<int:product_id>/', graph_recommendations), # Neo4j Graph mới
    path('api/chat/', chat_with_bot),
]