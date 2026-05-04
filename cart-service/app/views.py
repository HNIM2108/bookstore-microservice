from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .authentication import MicroserviceJWTAuthentication
from .models import CartItem
from .serializers import CartItemSerializer

# 1. API Xem toàn bộ giỏ hàng
class CartListView(APIView):
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user.id chính là id lấy từ Token đã giải mã
        items = CartItem.objects.filter(user_id=request.user.id)
        serializer = CartItemSerializer(items, many=True)
        return Response({
            "message": "Lấy giỏ hàng thành công",
            "total_distinct_items": items.count(),
            "cart": serializer.data
        })

# 2. API Thêm vào giỏ (Cộng thì thêm)
class AddToCartView(APIView):
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        # Lấy số lượng khách muốn thêm, mặc định là 1 nếu không điền
        qty_to_add = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({"error": "Thiếu product_id"}, status=400)

        # Tuyệt chiêu get_or_create: Tìm sản phẩm. Nếu chưa có, tạo mới luôn.
        item, created = CartItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=product_id,
            defaults={'quantity': qty_to_add}
        )

        # Nếu nó ĐÃ CÓ TỪ TRƯỚC (not created), thì mình CỘNG DỒN
        if not created:
            item.quantity += qty_to_add
            item.save()

        return Response({
            "message": "Đã thêm vào giỏ hàng", 
            "product_id": product_id,
            "current_quantity": item.quantity
        }, status=200)

# 3. API Bớt khỏi giỏ (Trừ thì bớt, Hết thì xóa)
class RemoveFromCartView(APIView):
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        qty_to_remove = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({"error": "Thiếu product_id"}, status=400)

        try:
            # Tìm món hàng trong giỏ của ĐÚNG user này
            item = CartItem.objects.get(user_id=request.user.id, product_id=product_id)
            
            # Thực hiện phép TRỪ
            item.quantity -= qty_to_remove

            # Logic chốt chặn: Nếu trừ xong mà bằng 0 hoặc âm, XÓA LUÔN KHỎI DB
            if item.quantity <= 0:
                item.delete()
                return Response({
                    "message": "Đã xóa hoàn toàn sản phẩm khỏi giỏ hàng do số lượng về 0"
                }, status=200)
            
            # Nếu vẫn còn > 0 thì lưu lại số lượng mới
            item.save()
            return Response({
                "message": "Đã giảm số lượng", 
                "current_quantity": item.quantity
            }, status=200)

        except CartItem.DoesNotExist:
            return Response({"error": "Sản phẩm này không tồn tại trong giỏ của bạn"}, status=404)