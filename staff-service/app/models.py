from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default="Sales") # VD: Sales, Kho, CSKH