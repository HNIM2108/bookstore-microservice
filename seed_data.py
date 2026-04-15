import requests
import json

CUSTOMER_URL = "http://localhost:8001/customers/"
BOOK_URL = "http://localhost:8002/books/"

# 1. TẠO KHÁCH HÀNG
customers = [
    {"name": "Nhật Minh", "email": "minh@gmail.com"},
    {"name": "Nguyễn Văn A", "email": "nguyenvana@gmail.com"}
]

print("--- ĐANG TẠO KHÁCH HÀNG ---")
for c in customers:
    res = requests.post(CUSTOMER_URL, json=c)
    if res.status_code == 201:
        print(f"✅ Đã tạo: {c['name']}")
    else:
        print(f"❌ Lỗi: {res.text}")

# 2. TẠO DANH SÁCH 15 CUỐN SÁCH
books = [
    {"title": "Clean Code", "author": "Robert C. Martin", "price": 45.00, "stock": 50},
    {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "price": 42.50, "stock": 40},
    {"title": "Design Patterns", "author": "David Thomas", "price": 50.00, "stock": 35},
    {"title": "Deep Learning với Python", "author": "Francois Chollet", "price": 35.00, "stock": 20},
    {"title": "Machine Learning cơ bản", "author": "Andrew Ng", "price": 38.00, "stock": 15},
    {"title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "price": 12.00, "stock": 100},
    {"title": "Nhà Giả Kim", "author": "Paulo Coelho", "price": 10.00, "stock": 120},
    {"title": "Sapiens: Lược Sử Loài Người", "author": "Yuval Noah Harari", "price": 18.00, "stock": 80},
    {"title": "Tư Duy Nhanh Và Chậm", "author": "Daniel Kahneman", "price": 20.00, "stock": 60},
    {"title": "Atomic Habits", "author": "Daniel Kahneman", "price": 22.00, "stock": 55},
    {"title": "Python for Data Analysis", "author": "Wes McKinney", "price": 40.00, "stock": 30},
    {"title": "Grokking Algorithms", "author": "Aditya Bhargava", "price": 30.00, "stock": 45},
    {"title": "Harry Potter và Hòn đá Phù thủy", "author": "J.K. Rowling", "price": 15.00, "stock": 200},
    {"title": "Chúa tể những chiếc nhẫn", "author": "J.R.R. Tolkien", "price": 25.00, "stock": 150},
    {"title": "Bố Già", "author": "Mario Puzo", "price": 14.00, "stock": 90}
]

print("\n--- ĐANG TẠO SÁCH MẪU ---")
for b in books:
    res = requests.post(BOOK_URL, json=b)
    if res.status_code == 201:
        print(f"✅ Đã tạo: {b['title']}")
    else:
        print(f"❌ Lỗi: {res.text}")