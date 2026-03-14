from django.db import models

class Manager(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100) # VD: Giám đốc kinh doanh, Trưởng phòng