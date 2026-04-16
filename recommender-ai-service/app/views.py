from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
import numpy as np

# Load sẵn mô hình và Vector lên RAM khi server khởi động
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
index = faiss.read_index('book_index.bin')
df_meta = pd.read_pickle('book_metadata.pkl')

@api_view(['GET'])
def recommend_similar_books(request, book_id):
    # 1. Tìm thông tin cuốn sách khách đang xem
    book_row = df_meta[df_meta['id'] == book_id]
    if book_row.empty:
        return Response({"error": "Sách không tồn tại"}, status=404)
    
    # 2. Lấy nội dung text của sách đó và biến thành Vector
    target_text = book_row.iloc[0]['text']
    target_vector = model.encode([target_text]).astype('float32')
    
    # 3. Nhờ FAISS tìm 3 cuốn gần nhất (bao gồm cả chính nó)
    distances, indices = index.search(target_vector, 3)
    
    # 4. Lọc kết quả (loại bỏ cuốn sách hiện tại ra khỏi danh sách gợi ý)
    recommended_books = []
    for idx in indices[0]:
        sim_book = df_meta.iloc[idx]
        if sim_book['id'] != book_id:
            recommended_books.append({
                # Ép kiểu int/str để đề phòng lỗi format JSON của thư viện Numpy
                "id": int(sim_book['id']), 
                "title": str(sim_book['title']),
                # Dùng .get() để chống lỗi KeyError, lấy author hoặc chữ mặc định
                "category": str(sim_book.get('category', sim_book.get('author', 'Sách liên quan')))
            })
            
    # Trả về tối đa 2 cuốn
    return Response(recommended_books[:2])

class RecommendBooks(APIView):
    def get(self, request, customer_id):
        # Trong thực tế, AI sẽ lấy lịch sử mua hàng và đánh giá để phân tích.
        # Ở đây, chúng ta trả về một danh sách gợi ý mẫu (Mock Data).
        recommendations = [
            {"book_id": 1, "reason": "Vì bạn đã mua sách về Django"},
            {"book_id": 2, "reason": "Sách bán chạy nhất tuần này"}
        ]

        return Response({
            "message": f"Hệ thống AI gợi ý sách cho khách hàng ID: {customer_id}",
            "recommendations": recommendations
        }, status=200)