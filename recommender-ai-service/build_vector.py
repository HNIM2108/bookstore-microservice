import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests

print("⏳ Đang khởi động mô hình NLP...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("🌐 Đang kết nối Book Service lấy dữ liệu thật...")
try:
    # Gọi API nội bộ của Book Service (Lưu ý: thay đổi URL nếu API danh sách sách của bạn khác)
    response = requests.get('http://book-service:8000/api/books/')
    books = response.json()
    
    if not books:
        print("⚠️ Cảnh báo: Book Service chưa có sách nào!")
    else:
        df = pd.DataFrame(books)
        
        # Gom các trường văn bản lại để nhúng Vector (Nếu model của bạn không có cột 'desc' thì bỏ ra nhé)
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
    print(f"❌ Lỗi khi lấy dữ liệu: {e}")