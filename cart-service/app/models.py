from django.db import models

class CartItem(models.Model):
    # CHÚ Ý: Dùng IntegerField, tuyệt đối không dùng ForeignKey
    user_id = models.IntegerField(help_text="ID của khách hàng từ User Service")
    product_id = models.IntegerField(help_text="ID của sản phẩm từ Product Service")
    
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} - Product {self.product_id} (x{self.quantity})"