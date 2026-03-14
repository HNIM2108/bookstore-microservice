from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shipment
from .serializers import ShipmentSerializer

class CreateShipment(APIView):
    # Thêm hàm GET để bạn có thể xem danh sách trên trình duyệt
    def get(self, request):
        shipments = Shipment.objects.all()
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tạo vận đơn thành công!", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)