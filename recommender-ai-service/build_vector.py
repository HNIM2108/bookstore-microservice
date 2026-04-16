import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests

print("⏳ Đang khởi động mô hình NLP...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("🌐 Đang kết nối Book Service lấy dữ liệu thật...")
try:
    # Đổi URL: Thử bỏ chữ /api/ đi, chỉ giữ lại /books/
    url = 'http://book-service:8000/books/'
    headers = {'Accept': 'application/json'}
    print(f"🌐 Đang kết nối tới: {url}")
    response = requests.get(url)
    
    # Kiểm tra xem Book Service có trả về lỗi 404/500 không
    if response.status_code != 200:
        print(f"❌ CẢNH BÁO: Book Service trả về mã lỗi {response.status_code}")
        print(f"Nội dung phản hồi: {response.text[:200]}") # In ra 200 ký tự HTML lỗi để dễ bắt bệnh
    else:
        books = response.json()
        
        if not books:
            print("⚠️ Cảnh báo: Book Service chưa có sách nào!")
        else:
            df = pd.DataFrame(books)
            # Gom các trường văn bản lại để nhúng Vector
            df['text'] = df['title'].astype(str) + " | " + df.get('author', '').astype(str)
            
            print(f"🧠 Đang Vector hóa {len(df)} cuốn sách...")
            embeddings = model.encode(df['text'].tolist())

            # Nhét vào FAISS
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(np.array(embeddings).astype('float32'))

            # Lưu lại
            faiss.write_index(index, 'book_index.bin')
            df.to_pickle('book_metadata.pkl')

            print("✅ Đã cập nhật Vector Index với dữ liệu THẬT từ Database!")
except Exception as e:
    print(f"❌ Lỗi hệ thống: {e}")