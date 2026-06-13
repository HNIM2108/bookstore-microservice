from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    category_id = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict) 

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name
