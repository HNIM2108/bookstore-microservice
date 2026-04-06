import os
import django
import pika
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')
django.setup()

from app.models import Order

def callback(ch, method, properties, body):
    data = json.loads(body)
    order_id = data['order_id']
    new_status = data['status']

    try:
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
        print(f"\n✅ ĐÃ CẬP NHẬT TRẠNG THÁI ORDER #{order_id} THÀNH: {new_status.upper()}")
    except Order.DoesNotExist:
        print(f"Không tìm thấy Order #{order_id} để cập nhật.")

    ch.basic_ack(delivery_tag=method.delivery_tag)

credentials = pika.PlainCredentials('admin', '123456')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='order_status_queue', durable=True)
channel.basic_consume(queue='order_status_queue', on_message_callback=callback)

print(" [*] Order Service đang túc trực chờ cập nhật trạng thái. Ấn CTRL+C để thoát.")
channel.start_consuming()