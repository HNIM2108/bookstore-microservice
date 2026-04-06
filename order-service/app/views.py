import pika
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer

# Hàm hỗ trợ: Gửi tin nhắn vào RabbitMQ
def publish_message(queue_name, message):
    try:

        # 1. Khai báo tài khoản / mật khẩu
        credentials = pika.PlainCredentials('admin', '123456')

        # 2. Gắn chìa khóa vào kết nối
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        # Kết nối tới RabbitMQ đang chạy trên Docker (localhost:5672)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Đảm bảo hàng đợi (queue) tồn tại. durable=True giúp giữ tin nhắn kể cả khi RabbitMQ khởi động lại
        channel.queue_declare(queue=queue_name, durable=True)

        # Gửi tin nhắn
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Đánh dấu tin nhắn là kiên định (Persistent)
            ))
        connection.close()
    except Exception as e:
        print(f"LỖI KẾT NỐI RABBITMQ: {e}")

class CreateOrder(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()

            pay_method = request.data.get("payment_method", "COD")
            ship_method = request.data.get("shipping_method", "Standard")
            address = request.data.get("address", "Hà Nội")

            # 1. Tạo gói tin (Payload) cho Thanh toán
            pay_payload = {
                "order_id": order.id,
                "method": pay_method,
                "amount": str(order.total_amount)
            }

            # 2. Tạo gói tin (Payload) cho Giao hàng
            ship_payload = {
                "order_id": order.id,
                "method": ship_method,
                "address": address
            }

            print("--- ĐANG BẮN SỰ KIỆN TỚI PAYMENT QUEUE ---")
            publish_message('payment_queue', pay_payload)

            print("--- ĐANG BẮN SỰ KIỆN TỚI SHIPPING QUEUE ---")
            publish_message('shipping_queue', ship_payload)

            # Phản hồi ngay lập tức cho khách hàng mà không cần chờ Pay/Ship xử lý xong!
            return Response({
                "message": "Đã nhận đơn hàng (Pending)! Hệ thống đang xử lý bất đồng bộ.",
                "order_id": order.id
            }, status=201)

        return Response(serializer.errors, status=400)