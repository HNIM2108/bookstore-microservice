from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer
import requests

# ĐƯỜNG DẪN CHUẨN (Không có ngoặc vuông/ngoặc đơn)
PAY_SERVICE_URL = "http://127.0.0.1:8005/payments/"
SHIP_SERVICE_URL = "http://127.0.0.1:8006/shipments/"

class CreateOrder(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()

            pay_method = request.data.get("payment_method", "COD")
            ship_method = request.data.get("shipping_method", "Standard")
            address = request.data.get("address", "Hà Nội")

            # 1. GỌI DỊCH VỤ THANH TOÁN
            try:
                requests.post(PAY_SERVICE_URL, json={
                    "order_id": order.id,
                    "method": pay_method,
                    "amount": str(order.total_amount)
                }, timeout=3)
            except requests.exceptions.RequestException as e:
                print("Lỗi gọi Pay Service:", e)

            # 2. GỌI DỊCH VỤ GIAO HÀNG
            try:
                requests.post(SHIP_SERVICE_URL, json={
                    "order_id": order.id,
                    "method": ship_method,
                    "address": address
                }, timeout=3)
            except requests.exceptions.RequestException as e:
                print("Lỗi gọi Ship Service:", e)

            return Response({
                "message": "Đã đặt hàng! Đang xử lý thanh toán và giao hàng.",
                "order_id": order.id
            }, status=201)

        return Response(serializer.errors, status=400)