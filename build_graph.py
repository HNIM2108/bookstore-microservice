from neo4j import GraphDatabase
import requests

# Cấu hình kết nối
API_URL = "http://127.0.0.1:8013/products/"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_graph(self, products):
        print("⏳ Đang dệt mạng lưới đồ thị tri thức...")
        with self.driver.session() as session:
            # 1. Xóa sạch dữ liệu cũ (nếu có) để làm lại từ đầu
            session.run("MATCH (n) DETACH DELETE n")
            
            # 2. Tạo Node Khách hàng VIP
            session.run("MERGE (u:User {id: 1, name: 'Nhật Minh'})")

            # 3. Quét từng sản phẩm để tạo Nút và Mối quan hệ
            for p in products:
                prod_id = p['id']
                name = p['name']
                cat_id = p['category_id']
                
                # Trích xuất dữ liệu từ cột JSON attributes
                attrs = p.get('attributes', {})
                brand = attrs.get('brand', attrs.get('author', 'Không rõ Hãng/Tác giả'))

                # Gắn nhãn danh mục cho dễ nhìn
                cat_name = {1: "Laptop", 2: "Điện thoại", 3: "Sách", 4: "Thời trang", 5: "Phụ kiện"}.get(cat_id, "Khác")

                # Câu lệnh Cypher "thần thánh" để vẽ đồ thị
                query = """
                // Tạo Node Sản phẩm
                MERGE (prod:Product {id: $prod_id, name: $name})

                // Tạo/Tìm Node Danh mục và nối BELONGS_TO
                MERGE (c:Category {id: $cat_id, name: $cat_name})
                MERGE (prod)-[:BELONGS_TO]->(c)

                // Tạo/Tìm Node Hãng và nối PRODUCED_BY
                MERGE (b:Brand {name: $brand})
                MERGE (prod)-[:PRODUCED_BY]->(b)
                """
                session.run(query, prod_id=prod_id, name=name, cat_id=cat_id, cat_name=cat_name, brand=brand)

            # 4. Tạo tương tác giả định giữa User và Product để test RAG
            session.run("""
            MATCH (u:User {id: 1})
            MATCH (p_mac:Product {name: 'MacBook Pro M3'})
            MATCH (p_s24:Product {name: 'Samsung Galaxy S24 Ultra'})
            MATCH (p_book:Product {name: 'Clean Code'})
            
            MERGE (u)-[:BOUGHT]->(p_mac)
            MERGE (u)-[:VIEWED]->(p_s24)
            MERGE (u)-[:BOUGHT]->(p_book)
            """)
            print("✅ Đã dệt xong hoàn toàn Đồ thị tri thức E-commerce!")

if __name__ == "__main__":
    print("🌐 Đang kết nối Product Service lấy dữ liệu...")
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            product_data = response.json()
            builder = KnowledgeGraphBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
            builder.build_graph(product_data)
            builder.close()
        else:
            print("❌ Không lấy được dữ liệu. Kiểm tra lại cổng 8013.")
    except Exception as e:
        print(f"⚠️ Lỗi kết nối: {e}")