from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer

class ProcessPayment(APIView):
    # Thêm hàm GET để bạn có thể xem danh sách trên trình duyệt
    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Thanh toán thành công!", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)