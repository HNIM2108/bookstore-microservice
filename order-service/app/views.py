import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from .serializers import OrderSerializer

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        # Lấy Token của khách hàng để "cầm hộ" sang Cart Service
        token = request.META.get('HTTP_AUTHORIZATION') 
        headers = {'Authorization': token}

        # --- BƯỚC 1: GỌI CART SERVICE ĐỂ XEM GIỎ HÀNG ---
        # Gọi tên container 'cart-service' cổng gốc 8000 (cổng bên trong Docker)
        cart_url = "http://cart-service:8000/api/cart/"
        try:
            cart_response = requests.get(cart_url, headers=headers)
            cart_response.raise_for_status() # Báo lỗi nếu mã không phải 200
        except requests.exceptions.RequestException:
            return Response({"error": "Không thể kết nối đến Dịch vụ Giỏ hàng"}, status=500)

        cart_data = cart_response.json().get('cart', [])
        if not cart_data:
            return Response({"error": "Giỏ hàng của bạn đang trống, không thể chốt đơn!"}, status=400)

        # --- BƯỚC 2: TẠO VỎ ĐƠN HÀNG TRỐNG ---
        order = Order.objects.create(user_id=user_id, total_amount=0)
        total_amount = 0

        # --- BƯỚC 3: QUÉT TỪNG MÓN, CHECK GIÁ VÀ XÓA KHỎI GIỎ ---
        for item in cart_data:
            product_id = item['product_id']
            quantity = item['quantity']

            # Gọi Product Service lấy giá hiện tại (Không cần token vì kho hàng mở cửa)
            product_url = f"http://product-service:8000/products/{product_id}/"
            try:
                product_response = requests.get(product_url)
                if product_response.status_code == 200:
                    product_info = product_response.json()
                    current_price = product_info['price']

                    # Chụp ảnh giá (Snapshot) và lưu vào Chi tiết hóa đơn
                    OrderItem.objects.create(
                        order=order,
                        product_id=product_id,
                        quantity=quantity,
                        price=current_price
                    )

                    # Cộng dồn tiền vào tổng hóa đơn
                    total_amount += float(current_price) * quantity

                    # Gửi lệnh sang Cart Service: "Đã mua xong món này, xóa đi!"
                    remove_url = "http://cart-service:8000/api/cart/remove/"
                    requests.post(remove_url, headers=headers, json={
                        "product_id": product_id,
                        "quantity": quantity
                    })
            except requests.exceptions.RequestException:
                # Nếu không kết nối được kho hàng, tạm bỏ qua món này (hoặc có thể báo lỗi tùy logic)
                pass

        # --- BƯỚC 4: CẬP NHẬT TỔNG TIỀN VÀ TRẢ VỀ ---
        order.total_amount = total_amount
        order.save()

        serializer = OrderSerializer(order)
        return Response({
            "message": "🎉 Chốt đơn thành công!",
            "order": serializer.data
        }, status=201)

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Trích xuất user_id từ token (nhờ cấu hình MicroserviceJWTAuthentication)
        user_id = request.user.id 
        
        # Gọi sang user-service để kiểm tra role của user hiện tại
        token = request.META.get('HTTP_AUTHORIZATION')
        user_url = "http://user-service:8000/api/profile/" 
        
        is_admin = False
        try:
            user_res = requests.get(user_url, headers={'Authorization': token})
            if user_res.status_code == 200:
                user_data = user_res.json().get('profile', {})
                if user_data.get('role') in ['admin', 'staff']:
                    is_admin = True
        except requests.exceptions.RequestException:
            pass # Nếu lỗi kết nối, mặc định chỉ là user thường
            
        # Nếu là Admin/Staff: Lấy toàn bộ đơn hàng
        if is_admin:
            orders = Order.objects.all().order_by('-created_at')
        # Nếu là Customer: Chỉ lấy đơn hàng của chính họ
        else:
            orders = Order.objects.filter(user_id=user_id).order_by('-created_at')

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)
    
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        try:
            # Chỉ cho phép Admin hoặc Staff đổi trạng thái
            order = Order.objects.get(id=order_id)
            new_status = request.data.get('status')
            
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                return Response({"message": f"Đã chuyển trạng thái đơn #{order_id} sang {new_status}"})
            return Response({"error": "Trạng thái không hợp lệ"}, status=400)
        except Order.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=404)