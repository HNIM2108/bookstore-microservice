from django.db import models

# Bước 7.5.2: Định nghĩa bảng Cart và CartItem
class Cart(models.Model):
    customer_id = models.IntegerField()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book_id = models.IntegerField()
    quantity = models.IntegerField()
