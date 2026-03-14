from django.db import models

class Order(models.Model):
    customer_id = models.IntegerField()
    cart_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Created")
