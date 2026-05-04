from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('paid', 'Đã thanh toán'),
        ('shipped', 'Đang giao'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    # Tuyệt đối không ForeignKey, chỉ lưu user_id từ Token
    user_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - User {self.user_id} - {self.status}"

class OrderItem(models.Model):
    # Được phép dùng ForeignKey ở đây vì OrderItem và Order nằm chung 1 Database (order_db)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    # Chỉ lưu ID của Product
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField()
    
    # CHỐT CHẶN BẮT BUỘC: Lưu "Snapshot" (Ảnh chụp) của giá tiền
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá tại thời điểm mua")

    def __str__(self):
        return f"Order {self.order.id} - Product {self.product_id} (x{self.quantity})"