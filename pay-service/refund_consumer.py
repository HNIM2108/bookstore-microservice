import os
import django
import pika
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pay_service.settings')
django.setup()

from app.models import Payment

def notify_order_status(order_id, status):
    try:
        credentials = pika.PlainCredentials('admin', '123456')
        parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='order_status_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='order_status_queue',
            body=json.dumps({"order_id": order_id, "status": status}),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Lỗi gửi báo cáo Order: {e}")

def callback(ch, method, properties, body):
    data = json.loads(body)
    order_id = data['order_id']
    reason = data.get('reason', '')

    print(f"\n⚠️ NHẬN TÍN HIỆU SAGA ROLLBACK CHO ORDER: {order_id}")

    try:
        payment = Payment.objects.filter(order_id=order_id).first()
        if payment:
            payment.status = "Refunded"
            payment.save()
            print(f"💰 ĐÃ HOÀN TIỀN THÀNH CÔNG VÀO TÀI KHOẢN KHÁCH HÀNG (Order {order_id})")

            # --- BƯỚC MỚI: BÁO CÁO LẠI CHO ORDER SERVICE LÀ ĐƠN NÀY ĐÃ TẠCH ---
            print("--- ĐANG BÁO CÁO TRẠNG THÁI HỦY VỀ ORDER SERVICE ---")
            notify_order_status(order_id, "Failed")

        else:
            print("Không tìm thấy giao dịch hợp lệ để hoàn tiền.")
    except Exception as e:
        print(f"Lỗi database khi hoàn tiền: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

credentials = pika.PlainCredentials('admin', '123456')
parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='compensation_queue', durable=True)
channel.basic_consume(queue='compensation_queue', on_message_callback=callback)

print(" [*] Pay Service (Luồng Hoàn Tiền) đang túc trực. Ấn CTRL+C để thoát.")
channel.start_consuming()