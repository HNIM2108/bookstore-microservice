from django.db import models

# Bước 7.3.3: Định nghĩa cấu trúc bảng Customer trong Database
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
    
class BehaviorLog(models.Model):
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    action = models.CharField(max_length=50) # Ví dụ: 'view', 'add_to_cart'
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Khách {self.customer_id} - {self.action} - Sách {self.book_id}"