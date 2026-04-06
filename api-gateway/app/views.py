import json
import time
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render



def home_view(request):
    # Hàm này đơn giản là bốc file index.html ném ra màn hình
    return render(request, 'index.html')


# 1. Trỏ vào tên container và cổng nội bộ 8000
SERVICES = {
    'books': 'http://book-service:8000/books/',
    'orders': 'http://order-service:8000/orders/',
    # (Nếu bạn gọi các service khác thì cứ thêm vào đây theo công thức: 'http://tên-thư-mục:8000/đường-dẫn/')
}

# 2. Sửa đường dẫn sang Auth Service
AUTH_VERIFY_URL = 'http://auth-service:8000/api/token/verify/'

# Biến toàn cục đơn giản để làm Rate Limiting (Giới hạn request)
IP_TRACKER = {}

@csrf_exempt
def gateway_proxy(request, path):
    client_ip = request.META.get('REMOTE_ADDR')
    current_time = time.time()

    # --- YÊU CẦU 1: LOGGING (Ghi nhật ký) ---
    print(f"\n[GATEWAY LOG] {request.method} request từ IP {client_ip} đi tới mục tiêu: /{path}")

    # --- YÊU CẦU 2: RATE LIMITING (Giới hạn tốc độ) ---
    # Chống spam: Không cho phép 1 IP gọi quá 5 request trong vòng 10 giây
    if client_ip in IP_TRACKER:
        requests_done, start_time = IP_TRACKER[client_ip]
        if current_time - start_time < 10:
            if requests_done >= 5:
                print("❌ BỊ CHẶN: Spam quá nhanh!")
                return JsonResponse({'error': 'Rate limit exceeded! Vui lòng chậm lại.'}, status=429)
            IP_TRACKER[client_ip] = (requests_done + 1, start_time)
        else:
            IP_TRACKER[client_ip] = (1, current_time)
    else:
        IP_TRACKER[client_ip] = (1, current_time)

    # --- YÊU CẦU 3: AUTHENTICATION VALIDATION (Kiểm tra thẻ JWT) ---
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print("❌ BỊ CHẶN: Không xuất trình thẻ JWT.")
        return JsonResponse({'error': 'Bạn phải có thẻ JWT (Bearer Token) để qua cổng!'}, status=401)

    token = auth_header.split(' ')[1]

    # Mang thẻ sang Auth Service (cổng 8012) nhờ kiểm tra xem thẻ giả hay thật
    verify_response = requests.post(AUTH_VERIFY_URL, json={'token': token})

    if verify_response.status_code != 200:
        # In thêm chi tiết lỗi từ Auth Service để dễ debug
        print(f"❌ BỊ CHẶN: Thẻ JWT bị Auth-Service từ chối. Lỗi trả về: {verify_response.text}")
        return JsonResponse({'error': 'Token không hợp lệ hoặc đã hết hạn!'}, status=401)

    # --- YÊU CẦU 4: ROUTING (Điều hướng luồng đi) ---
    service_name = path.split('/')[0] # Lấy chữ đầu tiên, VD: 'books'

    if service_name not in SERVICES:
        return JsonResponse({'error': 'Dịch vụ này không tồn tại trên hệ thống.'}, status=404)

    # Lắp ráp đường dẫn cuối cùng
    # Lưu ý: Bỏ phần service_name ở path gốc để ghép nối chuẩn xác
    target_path = path[len(service_name):]
    if target_path.startswith('/'):
        target_path = target_path[1:]

    target_url = f"{SERVICES[service_name]}{target_path}"
    print(f"✅ HỢP LỆ! Đang chuyển tiếp luồng dữ liệu tới: {target_url}")

    # Tiến hành chuyển tiếp (Forward Request)
    try:
        if request.method == 'GET':
            resp = requests.get(target_url, params=request.GET)
        elif request.method == 'POST':
            body = json.loads(request.body) if request.body else {}
            resp = requests.post(target_url, json=body)
        else:
            return JsonResponse({'error': 'Phương thức chưa được Gateway hỗ trợ'}, status=405)

        return HttpResponse(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI HẠ TẦNG: Service {service_name} đang sập!")
        return JsonResponse({'error': f'Service đích đang offline: {str(e)}'}, status=503)

def health_check(request):
    return JsonResponse({
        "service": "API Gateway",
        "status": "UP",
        "uptime": "100%",
        "message": "Hệ thống đang hoạt động trơn tru!"
    }, status=200)