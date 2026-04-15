from rest_framework import serializers
from .models import Customer
from .models import BehaviorLog

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__' # Lấy tất cả các trường (id, name, email)

class BehaviorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorLog
        fields = '__all__'