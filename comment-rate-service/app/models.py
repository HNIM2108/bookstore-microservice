from django.db import models

class Comment(models.Model):
    book_id = models.IntegerField()
    customer_id = models.IntegerField()
    rating = models.IntegerField() # Đánh giá từ 1 đến 5 sao
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
