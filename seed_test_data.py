import os
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mock Makale Verisi
sample_title = "YOLOv9 ve Edge AI Mimarisinde Gerçek Zamanlı Nesne Tespiti"
sample_summary = [
    "Saha görsellerinde %30 daha hızlı nesne tespiti sağlayan yeni mimari sunulmuştur.",
    "Edge cihazlarda bellek tüketimini yarı yarıya düşüren kuantizasyon tekniği uygulanmıştır.",
    "Davision AI bilgisayarlı görü projeleriyle doğrudan entegre edilebilir altyapı hazırlanmıştır."
]

# Vektör Embedding Üretme
embedding_res = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=sample_title + " " + " ".join(sample_summary)
)
vector = embedding_res.data[0].embedding

# Supabase'e Veri Ekleme
data = {
    "title": sample_title,
    "url": "https://arxiv.org/abs/2304.08485",
    "author": "Davision AI Ar-Ge Ekibi",
    "summary_bullets": sample_summary,
    "relevance_score": 8.8,
    "primary_category": "Computer Vision",
    "tags": ["YOLO", "Edge AI", "Computer Vision"],
    "embedding": vector,
    "is_dispatched": False
}

res = supabase.table("articles").insert(data).execute()
print("✅ Test makalesi Supabase'e başarıyla eklendi! ID:", res.data[0]['id'])