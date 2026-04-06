import os
import django
import pika
import json

# Thiết lập môi trường để có thể thao tác với Database của Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pay_service.settings')
django.setup()

from app.models import Payment

# Hàm xử lý khi có tin nhắn bay tới
def callback(ch, method, properties, body):
    print("\n--- ĐÃ NHẬN TIN NHẮN TỪ RABBITMQ ---")
    data = json.loads(body)

    # Tự động lưu vào Database
    Payment.objects.create(
        order_id=data['order_id'],
        method=data['method'],
        amount=data['amount'],
        status="Success" # Tạm thời để mặc định là Success
    )
    print(f"✅ Đã xử lý thanh toán thành công cho Order ID: {data['order_id']}")

    # Báo cáo lại cho RabbitMQ là "Tôi đã làm xong, hãy xóa tin nhắn đó khỏi hàng đợi đi"
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Kết nối RabbitMQ
credentials = pika.PlainCredentials('admin', '123456')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='payment_queue', durable=True)

# Bắt đầu lắng nghe
channel.basic_consume(queue='payment_queue', on_message_callback=callback)

print(" [*] Pay Service đang túc trực lắng nghe RabbitMQ. Ấn CTRL+C để thoát.")
channel.start_consuming()