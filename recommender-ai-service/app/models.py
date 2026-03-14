from rest_framework.views import APIView
from rest_framework.response import Response

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