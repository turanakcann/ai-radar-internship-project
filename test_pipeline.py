import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# 1. Environment Değişkenlerini Yükle
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("🔍 ENV Kontrolü:")
print(f" - Supabase URL: {'✅ Var' if SUPABASE_URL else '❌ Eksik'}")
print(f" - Supabase Key: {'✅ Var' if SUPABASE_SERVICE_ROLE_KEY else '❌ Eksik'}")
print(f" - OpenAI Key: {'✅ Var' if OPENAI_API_KEY else '❌ Eksik'}")
print(f" - Telegram Token: {'✅ Var' if TELEGRAM_BOT_TOKEN else '❌ Eksik'}\n")

# --- TEST 1: SUPABASE BAĞLANTISI ---
def test_supabase():
    print("🚀 Test 1: Supabase Bağlantısı Test Ediliyor...")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        # articles tablosuna hafif bir sorgu atalım
        response = supabase.table("articles").select("id").limit(1).execute()
        print("   ✅ Supabase Bağlantısı Başarılı!")
        return supabase
    except Exception as e:
        print(f"   ❌ Supabase Hatası: {e}")
        return None

# --- TEST 2: LLM & EMBEDDING (OPENAI) ---
def test_llm():
    print("\n🚀 Test 2: OpenAI LLM ve Embedding Test Ediliyor...")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 1. LLM Chat Completion Testi
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Davision AI Tech Radar projesi için tek cümlelik bir selam yaz."}]
        )
        print(f"   🤖 LLM Yanıtı: {chat_completion.choices[0].message.content}")

        # 2. Embedding Testi (pgvector için)
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input="Computer Vision and LLM integration test"
        )
        vec_len = len(embedding_response.data[0].embedding)
        print(f"   📐 Embedding Başarılı! Vektör Boyutu: {vec_len} (Beklenen: 1536)")
        return True
    except Exception as e:
        print(f"   ❌ OpenAI API Hatası: {e}")
        return False

# --- TEST 3: TELEGRAM DISPATCHER WEBHOOK ---
def test_telegram():
    print("\n🚀 Test 3: Telegram Dispatcher Test Ediliyor...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("   ⚠️ Telegram konfigürasyonu eksik, bu adım atlanıyor.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🧪 *Tech Radar Sistem Testi*\n\nLLM, Supabase ve Telegram entegrasyonu başarıyla çalışıyor\\!",
        "parse_mode": "MarkdownV2"
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        print("   📩 Telegram Bildirimi Başarıyla Gönderildi!")
        return True
    except Exception as e:
        print(f"   ❌ Telegram Hatası: {e}")
        return False

if __name__ == "__main__":
    sp = test_supabase()
    llm = test_llm()
    tg = test_telegram()
    
    print("\n" + "="*40)
    if sp and llm:
        print("🎉 TÜM TEMEL ENTEGRASYONLAR BAŞARIYLA ÇALIŞIYOR!")
    else:
        print("⚠️ Bazı testlerde hata alındı. Lütfen .env değişkenlerini kontrol edin.")
    print("="*40)