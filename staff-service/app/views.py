from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Staff
from .serializers import StaffSerializer
import requests

BOOK_SERVICE_URL = "http://localhost:8002/books/"

# Quản lý danh sách nhân viên
class StaffListCreate(APIView):
    def get(self, request):
        staffs = Staff.objects.all()
        serializer = StaffSerializer(staffs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# Chức năng: Nhân viên thêm sách mới vào hệ thống
class StaffManageBook(APIView):
    def post(self, request):
        staff_id = request.data.get("staff_id")
        book_data = request.data.get("book_data") # JSON chứa thông tin sách

        # Kiểm tra xem nhân viên có tồn tại không
        if not Staff.objects.filter(id=staff_id).exists():
            return Response({"error": "Nhân viên không hợp lệ!"}, status=403)

        # Gọi sang Book Service để thêm sách
        try:
            r = requests.post(BOOK_SERVICE_URL, json=book_data)
            if r.status_code == 201:
                return Response({"message": "Nhân viên đã thêm sách thành công!", "book": r.json()}, status=201)
            return Response({"error": "Lỗi từ Book Service", "details": r.json()}, status=400)
        except requests.exceptions.RequestException:
            return Response({"error": "Không thể kết nối đến Book Service"}, status=503)