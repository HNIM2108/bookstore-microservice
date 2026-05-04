from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Hàm này giống hệt ManagerListCreate cũ của bạn, nhưng dùng cho User chung
class UserRegisterView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tạo tài khoản thành công!", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    

class UserProfileView(APIView):
    # CHỐT CHẶN: Chỉ những người có Token hợp lệ mới được vào
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user lúc này đã được JWT tự động nhận diện từ Token
        serializer = UserSerializer(request.user)
        return Response({
            "message": "Lấy thông tin hồ sơ thành công!",
            "profile": serializer.data
        })