import os
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle

API_URL = 'http://product-service:8000/products/' # Đã đổi sang product
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

def build_vector_db():
    print("🌐 Đang kết nối Product Service lấy dữ liệu...")
    try:
        response = requests.get(API_URL)
        products = response.json()
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu: {e}")
        return

    if not products:
        print("⚠️ Không có sản phẩm nào để Vector hóa.")
        return

    df = pd.DataFrame(products)

    # 🌟 VŨ KHÍ BÍ MẬT Ở ĐÂY: Biến toàn bộ JSON attributes thành chuỗi text
    # Ví dụ: {'ram': '16GB', 'cpu': 'i7'} -> "{'ram': '16GB', 'cpu': 'i7'}"
    df['attributes_str'] = df['attributes'].astype(str)
    
    # Gom Tên sản phẩm + Thuộc tính để đưa cho AI học
    df['text_to_vectorize'] = df['name'] + " " + df['attributes_str']

    print("⏳ Đang tải mô hình NLP...")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"🧠 Đang mã hóa {len(df)} sản phẩm thành Vector...")
    embeddings = model.encode(df['text_to_vectorize'].tolist())

    # Tạo FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Lưu lại
    faiss.write_index(index, 'product_index.bin') # Đổi tên file
    with open('product_metadata.pkl', 'wb') as f: # Đổi tên file
        pickle.dump(df, f)

    print("✅ Đã cập nhật Vector Index cho Sản Phẩm thành công!")

if __name__ == "__main__":
    build_vector_db()