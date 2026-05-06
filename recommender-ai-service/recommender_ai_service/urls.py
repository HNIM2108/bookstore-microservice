from django.contrib import admin
from django.urls import path
from app.views import chat_with_bot, personalized_recommendations, recommend_similar_books
from app.views import recommend_similar_books, graph_recommendations
from app.views import TrackBehaviorView, BehaviorHistoryView

urlpatterns = [
    path('admin/', admin.site.urls),
    # ĐÂY LÀ DÒNG QUAN TRỌNG NHẤT: Khớp với Frontend và trỏ vào hàm AI thật
    path('api/recommend/<int:book_id>/', recommend_similar_books),
    path('api/graph-recommend/<int:product_id>/', graph_recommendations), # Neo4j Graph mới
    path('api/chat/', chat_with_bot),
    path('api/customers/track/', TrackBehaviorView.as_view(), name='track-behavior'),
    path('api/customers/<int:customer_id>/behavior/', BehaviorHistoryView.as_view(), name='behavior-history'),
    path('api/customers/<int:customer_id>/recommendations/', personalized_recommendations),
]