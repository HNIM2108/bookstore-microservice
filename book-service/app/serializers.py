from rest_framework import serializers
from .models import Book

# Bước chuyển đổi dữ liệu Sách sang định dạng JSON
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'