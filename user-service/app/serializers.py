from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Gộp các trường chuẩn và trường copy từ Manager vào
        fields = ['id', 'username', 'email', 'password', 'role', 'department']
        
        # BẮT BUỘC: Giấu mật khẩu, không trả về khi GET, chỉ dùng khi POST
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Hàm này thay thế hàm save() mặc định để mã hóa mật khẩu
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role', 'customer'),
            department=validated_data.get('department', '')
        )
        # Hàm set_password giúp băm (hash) mật khẩu thay vì lưu chữ thường
        user.set_password(validated_data['password'])
        user.save()
        return user