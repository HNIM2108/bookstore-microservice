from rest_framework_simplejwt.authentication import JWTAuthentication

class StatelessUser:
    """Phiên bản User ảo nâng cấp, đánh lừa Django tuyệt đối"""
    def __init__(self, user_id):
        self.id = user_id
        self.pk = user_id  # Django rất hay tìm kiếm thuộc tính pk này
        self.is_authenticated = True
        self.is_active = True # Bắt buộc phải có để qua mặt IsAuthenticated

    def __str__(self):
        return f"StatelessUser(id={self.id})"

class MicroserviceJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Trích xuất user_id từ Token
        user_id = validated_token.get('user_id')
        
        # IN LOG RA CONSOLE ĐỂ DEBUG
        print("="*50)
        print(f"🚀 [DEBUG] Cart-Service đã giải mã Token!")
        print(f"🚀 [DEBUG] Nhận diện được user_id: {user_id}")
        print("="*50)
        
        return StatelessUser(user_id)