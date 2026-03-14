from django.db import models

class Payment(models.Model):
    order_id = models.IntegerField()
    method = models.CharField(max_length=50) # Ví dụ: Momo, Credit Card, COD
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Success")