import requests

# Gọi thẳng vào cổng 8013 mà bạn vừa cấu hình cho product-service
API_URL = "http://127.0.0.1:8013/products/"

products = [
    # --- Category 1: Laptop ---
    {
        "name": "MacBook Pro M3", "category_id": 1, "price": 2000.00, "stock": 15, 
        "attributes": {"brand": "Apple", "ram": "16GB", "cpu": "M3 Pro", "screen": "14 inch"}
    },
    {
        "name": "Dell XPS 15", "category_id": 1, "price": 1800.00, "stock": 10, 
        "attributes": {"brand": "Dell", "ram": "32GB", "cpu": "Core i7", "screen": "15.6 inch OLED"}
    },
    
    # --- Category 2: Điện thoại ---
    {
        "name": "iPhone 15 Pro Max", "category_id": 2, "price": 1200.00, "stock": 25, 
        "attributes": {"brand": "Apple", "storage": "256GB", "color": "Titanium Natural", "camera": "48MP"}
    },
    {
        "name": "Samsung Galaxy S24 Ultra", "category_id": 2, "price": 1150.00, "stock": 20, 
        "attributes": {"brand": "Samsung", "storage": "512GB", "color": "Titanium Black", "stylus": "S-Pen"}
    },
    
    # --- Category 3: Sách (Giữ lại tinh hoa cũ) ---
    {
        "name": "Clean Code", "category_id": 3, "price": 45.00, "stock": 50, 
        "attributes": {"author": "Robert C. Martin", "pages": 464, "language": "English"}
    },
    {
        "name": "Đắc Nhân Tâm", "category_id": 3, "price": 10.00, "stock": 100, 
        "attributes": {"author": "Dale Carnegie", "pages": 320, "language": "Vietnamese"}
    },
    
    # --- Category 4: Thời trang ---
    {
        "name": "Áo thun Polo Ralph Lauren", "category_id": 4, "price": 85.00, "stock": 40, 
        "attributes": {"brand": "Ralph Lauren", "size": "L", "color": "Navy Blue", "material": "Cotton"}
    },
    {
        "name": "Giày thể thao Nike Air Force 1", "category_id": 4, "price": 110.00, "stock": 30, 
        "attributes": {"brand": "Nike", "size": "42", "color": "White", "type": "Sneaker"}
    },
    
    # --- Category 5: Phụ kiện ---
    {
        "name": "Chuột không dây Logitech MX Master 3S", "category_id": 5, "price": 99.00, "stock": 60, 
        "attributes": {"brand": "Logitech", "type": "Wireless Mouse", "dpi": "8000"}
    },
    {
        "name": "Bàn phím cơ Keychron Q1 Pro", "category_id": 5, "price": 199.00, "stock": 15, 
        "attributes": {"brand": "Keychron", "type": "Mechanical Keyboard", "switch": "Brown"}
    }
]

def seed_data():
    print(f"🚀 Đang nạp {len(products)} sản phẩm vào Product Service...")
    success_count = 0
    for p in products:
        try:
            response = requests.post(API_URL, json=p)
            if response.status_code == 201:
                print(f"✅ Đã thêm: {p['name']}")
                success_count += 1
            else:
                print(f"❌ Lỗi khi thêm {p['name']}: {response.text}")
        except Exception as e:
            print(f"⚠️ Lỗi kết nối: {e}")
    
    print(f"\n🎉 Hoàn tất! Nạp thành công {success_count}/{len(products)} sản phẩm.")

if __name__ == "__main__":
    seed_data()