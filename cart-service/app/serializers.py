from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'user_id', 'product_id', 'quantity', 'added_at']
        # Đảm bảo không ai hack được user_id truyền từ postman, user_id phải lấy từ Token
        read_only_fields = ['user_id', 'added_at']