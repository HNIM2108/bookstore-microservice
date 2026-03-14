from django.db import models

# Bước 7.3.3: Định nghĩa cấu trúc bảng Customer trong Database
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name