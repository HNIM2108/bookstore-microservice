import os
import django
import pika
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_service.settings')
django.setup()

from app.models import Shipment

# Hàm bắn tín hiệu HOÀN TIỀN (Saga Compensation)
def trigger_compensation(order_id):
    try:
        credentials = pika.PlainCredentials('admin', '123456')
        parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Tạo một hàng đợi chuyên dùng để xử lý sự cố hoàn tiền
        channel.queue_declare(queue='compensation_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='compensation_queue',
            body=json.dumps({"order_id": order_id, "reason": "Khu vực không hỗ trợ giao hàng"}),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Lỗi khi gửi yêu cầu hoàn tiền: {e}")

def callback(ch, method, properties, body):
    data = json.loads(body)
    address = data.get('address', '')
    order_id = data['order_id']

    # GIẢ LẬP LỖI SAGA: Không giao hàng ra Đảo
    if "Đảo" in address or "đảo" in address:
        print(f"\n❌ TỪ CHỐI GIAO HÀNG (Order {order_id}): Địa chỉ ngoài vùng phủ sóng.")
        print("--- ĐANG KÍCH HOẠT SAGA ROLLBACK (YÊU CẦU HOÀN TIỀN) ---")
        trigger_compensation(order_id)
    else:
        Shipment.objects.create(
            order_id=order_id,
            method=data['method'],
            address=address,
            status="Preparing"
        )
        print(f"\n📦 Đã lên đơn vận chuyển cho Order ID: {order_id}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

credentials = pika.PlainCredentials('admin', '123456')
parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='shipping_queue', durable=True)
channel.basic_consume(queue='shipping_queue', on_message_callback=callback)

print(" [*] Ship Service đang túc trực lắng nghe RabbitMQ. Ấn CTRL+C để thoát.")
channel.start_consuming()