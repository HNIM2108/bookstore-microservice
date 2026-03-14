from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
import requests

# URL của Cart Service.
# Hiện tại ta để localhost:8003 vì chạy trực tiếp trên máy (sau này dùng Docker sẽ đổi lại)
CART_SERVICE_URL = "http://127.0.0.1:8003"

# Bước 7.3.5: Tạo View xử lý GET (Lấy danh sách) và POST (Tạo khách hàng)
class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()

            # --- YÊU CẦU 4.3.1: Khi tạo Customer, phải tự động tạo Cart ---
            # Gọi API sang Cart-Service
            try:
                requests.post(
                    f"{CART_SERVICE_URL}/carts/",
                    json={"customer_id": customer.id},
                    timeout=3
                )
            except requests.exceptions.RequestException as e:
                # Đặt trong try/except để không bị sập nếu Cart Service chưa được bật
                print("Cảnh báo: Không thể gọi Cart Service. Chi tiết lỗi:", e)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
