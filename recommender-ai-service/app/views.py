from rest_framework.decorators import api_view
from rest_framework.response import Response
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import pandas as pd
from neo4j import GraphDatabase
import requests

# Khởi tạo kết nối Neo4j (Dùng tên container 'neo4j-db' làm host)
NEO4J_URI = "bolt://neo4j-db:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
model = SentenceTransformer(MODEL_NAME)

# Đọc file mới
INDEX_FILE = 'product_index.bin'
META_FILE = 'product_metadata.pkl'

index = None
df_meta = None

if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, 'rb') as f:
        df_meta = pickle.load(f)

@api_view(['GET'])
def recommend_similar_books(request, book_id):
    # Đổi tham số book_id thành product_id cho hợp logic, nhưng hàm vẫn giữ tên cũ cũng được
    product_id = book_id 
    
    if index is None or df_meta is None:
        return Response({"error": "Chưa có dữ liệu Vector."}, status=500)

    try:
        product_row = df_meta[df_meta['id'] == product_id]
        if product_row.empty:
            return Response({"error": "Sản phẩm không tồn tại."}, status=404)

        # Vector hóa thuộc tính của sản phẩm hiện tại
        query_text = str(product_row.iloc[0]['name']) + " " + str(product_row.iloc[0]['attributes'])
        query_vector = model.encode([query_text])

        # Tìm top 3 sản phẩm giống nhất (tính cả chính nó)
        distances, indices = index.search(query_vector, 3)

        recommended_products = []
        for idx in indices[0]:
            sim_product = df_meta.iloc[idx]
            if sim_product['id'] != product_id:
                # Đóng gói dữ liệu trả về
                attributes = sim_product.get('attributes', {})
                # Ưu tiên lấy brand hoặc author làm mô tả phụ
                sub_info = attributes.get('brand', attributes.get('author', "Sản phẩm liên quan"))
                
                recommended_products.append({
                    "id": int(sim_product['id']),
                    "name": str(sim_product['name']),
                    "author": str(sub_info), # Frontend đang dùng trường này để in chữ nhỏ
                    "price": float(sim_product['price']),
                    "category": int(sim_product['category_id'])
                })
                
        return Response(recommended_products[:2])
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
def graph_recommendations(request, product_id):
    """
    Tìm gợi ý bằng Đồ thị Tri thức (Collaborative Filtering).
    Logic: Tìm những User đã tương tác với product_id này, 
    sau đó xem họ đã tương tác với các sản phẩm nào khác.
    """
    query = """
    MATCH (target:Product {id: $prod_id})<-[:VIEWED|BOUGHT]-(u:User)-[:VIEWED|BOUGHT]->(other:Product)
    WHERE other.id <> $prod_id
    RETURN other.id AS id, other.name AS name, count(*) AS score
    ORDER BY score DESC LIMIT 3
    """
    
    try:
        with neo4j_driver.session() as session:
            result = session.run(query, prod_id=product_id)
            recommendations = []
            for record in result:
                recommendations.append({
                    "id": record["id"],
                    "name": record["name"],
                    "match_score": record["score"],
                    "reason": "Nhiều khách hàng khác cũng quan tâm"
                })
        
        return Response({"graph_recommendations": recommendations})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

# OLLAMA_API_URL = "http://ollama-service:11434/api/generate"
OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"

@api_view(['POST'])
def chat_with_bot(request):
    user_message = request.data.get('message', '')
    product_id = request.data.get('product_id', None)

    if not user_message:
        return Response({"error": "Vui lòng nhập tin nhắn"}, status=400)

    # 1. RETRIEVAL (Truy xuất tri thức từ Knowledge Graph)
    context = ""
    if product_id:
        query = """
        MATCH (p:Product {id: $prod_id})<-[:BOUGHT|ADDED_TO_CART]-(u:User)-[:BOUGHT|ADDED_TO_CART]->(other:Product)
        RETURN other.name AS name, count(*) AS score
        ORDER BY score DESC LIMIT 3
        """
        try:
            with neo4j_driver.session() as session:
                result = session.run(query, prod_id=int(product_id))
                recs = [str(record["name"]) for record in result if record["name"] is not None]
                if recs:
                    context = f"Thông tin nội bộ: Khách hàng đang xem sản phẩm ID {product_id}. Lịch sử hệ thống cho thấy những khách hàng khác xem sản phẩm này rất hay mua kèm các món sau: {', '.join(recs)}."
        except Exception as e:
            print("Lỗi Neo4j:", e)

    # 2. AUGMENTATION (Tăng cường ngữ cảnh vào Prompt)
    prompt = f"""Bạn là ULTRA AI, một trợ lý bán hàng lịch sự, chuyên nghiệp của hệ thống Ultra Tech.
    Quy tắc:
    - Trả lời bằng tiếng Việt, thân thiện và ngắn gọn.
    - {context}
    - Dựa vào Thông tin nội bộ (nếu có), hãy tư vấn chéo (cross-sell) một cách khéo léo cho khách hàng. Không cần nói lộ ra là hệ thống bảo thế.
    
    Khách hàng nói: "{user_message}"
    ULTRA AI:"""

    # 3. GENERATION (Nhờ Qwen2 sinh văn bản)
    try:
        payload = {
            "model": "qwen2:0.5b", # Đã chuyển sang model siêu nhẹ
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        reply = response.json().get('response', '')
        
        return Response({"reply": reply})
    except Exception as e:
        return Response({"error": f"Lỗi gọi LLM: {str(e)}"}, status=500)