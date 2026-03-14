from django.shortcuts import render
import requests

# Đổi 127.0.0.1 thành localhost để tránh lỗi phân giải DNS của Windows
BOOK_SERVICE_URL = "http://localhost:8002/books/"

def home(request):
    try:
        print("ĐANG GỌI TỚI:", BOOK_SERVICE_URL) # In ra terminal để theo dõi
        # Thêm timeout=5 để tránh việc bị treo (chờ mạng quá lâu)
        response = requests.get(BOOK_SERVICE_URL, timeout=5)

        print("MÃ TRẠNG THÁI (STATUS CODE):", response.status_code)

        if response.status_code == 200:
            books = response.json()
            print("LẤY DỮ LIỆU THÀNH CÔNG:", books)
        else:
            books = []
            print("LỖI DỮ LIỆU TỪ 8002:", response.text)

    except requests.exceptions.RequestException as e:
        # Nếu không gọi được, sẽ in ra dòng lỗi màu đỏ ở Terminal
        print("LỖI KẾT NỐI (LỄ TÂN KHÔNG GỌI ĐƯỢC BẾP):", e)
        books = []

    return render(request, 'index.html', {'books': books})