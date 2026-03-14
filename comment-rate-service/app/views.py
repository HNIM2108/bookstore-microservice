from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommentSerializer
import requests

BOOK_SERVICE_URL = "http://127.0.0.1:8002/books/"

class CommentCreate(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")

        # 1. Gọi sang Book Service để kiểm tra sách có tồn tại không
        try:
            r = requests.get(BOOK_SERVICE_URL)
            books = r.json()
            if not any(b["id"] == int(book_id) for b in books):
                return Response({"error": "Sách không tồn tại, không thể bình luận!"}, status=404)
        except requests.exceptions.RequestException:
            return Response({"error": "Không thể kết nối đến Book Service"}, status=503)

        # 2. Lưu bình luận
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)