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

# MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
# model = SentenceTransformer(MODEL_NAME)
import threading

# Tắt Telemetry để chống nhiễu mạng của Hugging Face
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

class AIModelManager:
    _model = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        with cls._lock:
            if cls._model is None:
                print("🚀 Đang khởi động AI Model từ ổ cứng...")
                cls._model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                print("✅ Nạp AI Model thành công!")
        return cls._model

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
        # query_vector = model.encode([query_text])
        # Vector hóa thuộc tính của sản phẩm hiện tại
        query_text = str(product_row.iloc[0]['name']) + " " + str(product_row.iloc[0]['attributes'])
        
        # Lấy model một cách an toàn và encode
        ai_model = AIModelManager.get_model()
        query_vector = ai_model.encode([query_text])

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

    context_str = ""

    # ==========================================
    # 1. TÌM KIẾM NGỮ NGHĨA (FAISS) TỪ CÂU HỎI
    # ==========================================
    try:
        if index is not None and df_meta is not None:
            # Biến câu hỏi của khách thành Vector
            # query_vector = model.encode([user_message])
            ai_model = AIModelManager.get_model()
            query_vector = ai_model.encode([user_message])
            # Tìm 3 sản phẩm khớp nhất trong kho
            distances, indices = index.search(query_vector, 3)
            
            found_products = []
            for idx in indices[0]:
                sim_product = df_meta.iloc[idx]
                brand = sim_product.get('attributes', {}).get('brand', 'Không rõ')
                found_products.append(f"{sim_product['name']} (Hãng: {brand}, Giá: ${sim_product['price']})")
            
            if found_products:
                context_str += f"\n- Sản phẩm trong kho khớp với yêu cầu: {', '.join(found_products)}."
    except Exception as e:
        print("Lỗi FAISS trong chat:", e)

    # ==========================================
    # 2. GỢI Ý MUA KÈM TỪ ĐỒ THỊ (NEO4J)
    # ==========================================
    if product_id:
        query = """
        MATCH (p:Product {id: $prod_id})<-[:BOUGHT|ADDED_TO_CART]-(u:User)-[:BOUGHT|ADDED_TO_CART]->(other:Product)
        WHERE other.name IS NOT NULL
        RETURN other.name AS name, count(*) AS score
        ORDER BY score DESC LIMIT 3
        """
        try:
            with neo4j_driver.session() as session:
                result = session.run(query, prod_id=int(product_id))
                recs = [str(record["name"]) for record in result if record["name"] is not None]
                if recs:
                    context_str += f"\n- Khách đang xem ID {product_id}, hãy gợi ý mua kèm: {', '.join(recs)}."
        except Exception as e:
            print("Lỗi Neo4j:", e)

    # ==========================================
    # 3. ÉP KHUÔN PROMPT CHO LLAMA 3.2
    # ==========================================
    prompt = f"""Bạn là ULTRA AI, một trợ lý bán hàng chuyên nghiệp của Ultra Tech.
    Quy tắc TỐI THƯỢNG:
    1. CHỈ ĐƯỢC tư vấn các sản phẩm có trong "Dữ liệu cửa hàng" dưới đây.
    2. Nếu Dữ liệu cửa hàng không có sản phẩm khách cần, hãy lịch sự nói rằng cửa hàng hiện không có hoặc đã hết hàng. Tuyệt đối KHÔNG tự bịa ra sản phẩm ngoài.
    3. Trả lời bằng tiếng Việt, ngắn gọn, thân thiện.

    Dữ liệu cửa hàng: {context_str if context_str else "Không tìm thấy sản phẩm phù hợp."}

    Khách hàng hỏi: "{user_message}"
    ULTRA AI:"""

    try:
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        reply = response.json().get('response', '')
        
        return Response({"reply": reply})
    except Exception as e:
        return Response({"error": f"Lỗi gọi LLM: {str(e)}"}, status=500)
    

    
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserBehavior

# API 1: Hứng dữ liệu khi khách click xem hàng (POST /customers/track/)
# API 1: Hứng dữ liệu khi khách click xem hàng (POST /customers/track/)
class TrackBehaviorView(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        product_id = data.get('book_id') or data.get('product_id')
        action = data.get('action')

        # 1. Lưu vào MySQL (Như cũ)
        UserBehavior.objects.create(
            customer_id=customer_id,
            product_id=product_id, 
            action=action
        )

        # 2. VẼ LÊN ĐỒ THỊ NEO4J (THÊM MỚI)
        # MERGE nghĩa là: Chưa có thì tạo, có rồi thì thôi
        neo4j_query = """
        MERGE (u:User {id: $user_id})
        MERGE (p:Product {id: $prod_id})
        MERGE (u)-[r:VIEWED]->(p)
        """
        try:
            with neo4j_driver.session() as session:
                session.run(neo4j_query, user_id=int(customer_id), prod_id=int(product_id))
        except Exception as e:
            print("Lỗi đồng bộ Neo4j:", e)

        return Response({"message": "Đã ghi nhận hành vi cho AI!"}, status=201)

# API 2: Trả dữ liệu về cho trang Profile (GET /customers/<id>/behavior/)
class BehaviorHistoryView(APIView):
    def get(self, request, customer_id):
        # Lấy 10 hành động gần nhất của user này
        logs = UserBehavior.objects.filter(customer_id=customer_id).order_by('-timestamp')[:10]
        data = [
            {
                "product_id": log.product_id,
                "action": log.action,
                "timestamp": log.timestamp
            } for log in logs
        ]
        return Response(data, status=200)
    
@api_view(['GET'])
def personalized_recommendations(request, customer_id):
    """
    Gợi ý Cá nhân hóa: Tìm những User có chung sở thích với customer_id, 
    xem họ thích gì khác và gợi ý.
    """
    query = """
    // 1. Tìm các sản phẩm mà User này đã xem
    MATCH (u:User {id: $user_id})-[:VIEWED|BOUGHT]->(p:Product)
    
    // 2. Tìm những User KHÁC cũng xem các sản phẩm giống vậy
    MATCH (p)<-[:VIEWED|BOUGHT]-(other_u:User)
    
    // 3. Xem những User kia còn xem thêm sản phẩm nào khác nữa
    MATCH (other_u)-[:VIEWED|BOUGHT]->(rec_p:Product)
    
    // 4. Lọc bỏ những sản phẩm mà User hiện tại đã xem rồi
    WHERE NOT (u)-[:VIEWED|BOUGHT]->(rec_p) AND rec_p.id IS NOT NULL
    
    // 5. Đếm số lần xuất hiện và xếp hạng
    RETURN rec_p.id AS id, count(*) AS score
    ORDER BY score DESC LIMIT 4
    """
    
    try:
        with neo4j_driver.session() as session:
            result = session.run(query, user_id=int(customer_id))
            recommendations = []
            for record in result:
                prod_id = record["id"]
                prod_name = f"Sản phẩm #{prod_id}"
                
                # Tra cứu tên thật từ file dữ liệu df_meta đã nạp sẵn
                if df_meta is not None:
                    try:
                        matched = df_meta[df_meta['id'] == int(prod_id)]
                        if not matched.empty:
                            prod_name = matched.iloc[0]['name']
                    except Exception:
                        pass

                recommendations.append({
                    "id": prod_id,
                    "name": prod_name,  # Đã có tên thật để gửi đi!
                    "match_score": record["score"],
                    "reason": "Dựa trên tệp khách hàng tương đồng"
                })
        return Response({"personalized_recs": recommendations})
    except Exception as e:
        return Response({"error": str(e)}, status=500)