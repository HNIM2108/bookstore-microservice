from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://127.0.0.1:8002/books/"

class CartCreate(APIView):
    # Thêm hàm GET để hiển thị danh sách giỏ hàng
    def get(self, request):
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class AddCartItem(APIView):
    # Thêm hàm GET để hiển thị danh sách các sản phẩm trong giỏ
    def get(self, request):
        items = CartItem.objects.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        book_id = request.data.get("book_id")

        try:
            r = requests.get(BOOK_SERVICE_URL)
            books = r.json()
            if not any(b["id"] == int(book_id) for b in books):
                return Response({"error": "Sách không tồn tại trong hệ thống"}, status=404)
        except requests.exceptions.RequestException:
            return Response({"error": "Không thể kết nối đến Book Service"}, status=503)

        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            items = CartItem.objects.filter(cart=cart)
            serializer = CartItemSerializer(items, many=True)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"error": "Không tìm thấy Giỏ hàng"}, status=404)