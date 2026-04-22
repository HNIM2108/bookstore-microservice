from neo4j import GraphDatabase
import requests
import random
from faker import Faker
import time

# Khởi tạo công cụ sinh tên tiếng Việt
fake = Faker('vi_VN')

# Cấu hình kết nối
API_URL = "http://product-service:8000/products/"
NEO4J_URI = "bolt://neo4j-db:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

def generate_knowledge_base():
    print("🌐 Đang lấy danh sách sản phẩm từ Product Service...")
    try:
        products = requests.get(API_URL).json()
        product_ids = [p['id'] for p in products]
        if not product_ids:
            print("❌ Không có sản phẩm nào! Hãy chạy file seed_products.py trước.")
            return
    except Exception as e:
        print(f"⚠️ Lỗi kết nối API: {e}")
        return

    print("👨‍👩‍👧‍👦 Đang sinh dữ liệu 1000 Khách hàng (Users)...")
    # Tạo sẵn user số 1 là Nhật Minh để giữ nguyên tài khoản test của bạn
    users = [{'id': 1, 'name': 'Nhật Minh', 'email': 'minh@gmail.com'}]
    for i in range(2, 1001):
        users.append({
            'id': i,
            'name': fake.name(),
            'email': fake.ascii_email()
        })

    print("🛒 Đang giả lập khoảng 10.000 hành vi mua sắm ngẫu nhiên...")
    viewed, carted, bought = [], [], []
    
    # Thiết lập tỷ lệ thực tế: Xem (70%), Thêm Giỏ (20%), Mua (10%)
    actions = ['VIEWED', 'ADDED_TO_CART', 'BOUGHT']
    weights = [0.7, 0.2, 0.1] 

    for user in users:
        # Mỗi người sẽ ngẫu nhiên dạo xem từ 5 đến 15 sản phẩm
        num_interactions = random.randint(5, 15)
        interacted_products = random.choices(product_ids, k=num_interactions)

        for prod_id in interacted_products:
            action = random.choices(actions, weights=weights, k=1)[0]
            if action == 'VIEWED': 
                viewed.append({'uid': user['id'], 'pid': prod_id})
            elif action == 'ADDED_TO_CART': 
                carted.append({'uid': user['id'], 'pid': prod_id})
            elif action == 'BOUGHT': 
                bought.append({'uid': user['id'], 'pid': prod_id})

    total_actions = len(viewed) + len(carted) + len(bought)
    print(f"⚡ Đã chuẩn bị xong {total_actions} tương tác. Chuẩn bị bơm vào Neo4j...")
    
    start_time = time.time()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Dọn dẹp User cũ (Giữ lại Node Product và Node Category)
        session.run("MATCH (u:User) DETACH DELETE u")

        # 2. Bơm 1000 User
        session.run("""
        UNWIND $users AS u
        MERGE (:User {id: u.id, name: u.name, email: u.email})
        """, users=users)

        # 3. Bơm các mối quan hệ (Cạnh)
        print("   -> Bơm dữ liệu VIEWED...")
        session.run("UNWIND $data AS r MATCH (u:User {id: r.uid}), (p:Product {id: r.pid}) MERGE (u)-[:VIEWED]->(p)", data=viewed)
        
        print("   -> Bơm dữ liệu ADDED_TO_CART...")
        session.run("UNWIND $data AS r MATCH (u:User {id: r.uid}), (p:Product {id: r.pid}) MERGE (u)-[:ADDED_TO_CART]->(p)", data=carted)
        
        print("   -> Bơm dữ liệu BOUGHT...")
        session.run("UNWIND $data AS r MATCH (u:User {id: r.uid}), (p:Product {id: r.pid}) MERGE (u)-[:BOUGHT]->(p)", data=bought)

    driver.close()
    elapsed = round(time.time() - start_time, 2)
    print(f"✅ HOÀN TẤT TUYỆT ĐỐI! Toàn bộ quá trình lưu vào CSDL mất {elapsed} giây.")

if __name__ == "__main__":
    generate_knowledge_base()