from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    # Lồng danh sách mặt hàng vào trong hóa đơn
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_amount', 'status', 'created_at', 'items']
        # Khóa các trường này lại, không cho khách hàng tự ý gửi giá tiền giả mạo lên
        read_only_fields = ['user_id', 'total_amount', 'status', 'created_at']