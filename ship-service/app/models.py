from django.db import models

class Shipment(models.Model):
    order_id = models.IntegerField()
    method = models.CharField(max_length=100) # Giao hàng nhanh, Hỏa tốc...
    address = models.TextField()
    status = models.CharField(max_length=50, default="Preparing")
