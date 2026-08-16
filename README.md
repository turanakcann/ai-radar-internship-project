<div align="center">

# 🚀 Davision AI Tech & Trend Radar

**Yapay Zeka ve Makine Öğrenimi alanındaki gelişmeleri takip eden, çok ajanlı otonom bir istihbarat platformu.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange.svg)](https://trychroma.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📸 Ekran Görüntüleri

### Ana Sayfa — Intelligence Feed
![Ana Sayfa Feed Görünümü](pictures/Screenshot%202026-08-16%20at%2021-45-08%20Davision%20AI%20Radar%20%E2%80%94%20Autonomous%20Intelligence%20Feed.png)

### Anlamsal Arama — Vector Intelligence Search
![Semantik Arama Sayfası](pictures/Screenshot%202026-08-16%20at%2021-45-17%20Davision%20AI%20Radar%20%E2%80%94%20Autonomous%20Intelligence%20Feed.png)

### Arama Sonuçları
![Arama Sonuçları](pictures/Screenshot%202026-08-16%20at%2021-45-27%20Davision%20AI%20Radar%20%E2%80%94%20Autonomous%20Intelligence%20Feed.png)

### Analytics Dashboard — Pipeline İstatistikleri
![Analytics Dashboard](pictures/Screenshot%202026-08-16%20at%2021-45-41%20Davision%20AI%20Radar%20%E2%80%94%20Autonomous%20Intelligence%20Feed.png)

### Telegram Bot Entegrasyonu
<div align="center">
<img src="pictures/WhatsApp%20Image%202026-08-16%20at%2021.41.48.jpeg" width="340" alt="Telegram Bot - Pipeline Başlatma"/>
<img src="pictures/WhatsApp%20Image%202026-08-16%20at%2021.41.48%20(1).jpeg" width="340" alt="Telegram Bot - Makale Bildirimi"/>
</div>

> Telegram botuna `/run` komutu gönderildiğinde pipeline tetiklenir ve yüksek puanlı makaleler otomatik olarak bottan iletilir.

---

## 📖 Proje Hakkında

**Davision AI Tech & Trend Radar**, ArXiv, Medium ve GitHub gibi kaynaklardan AI/ML alanındaki makaleleri ve projeleri otomatik olarak keşfeden, puanlayan, özetleyen ve Telegram üzerinden bildiren otonom bir çok-ajan sistemidir.

### ✨ Temel Özellikler

- 🔍 **Otomatik Tarama** — ArXiv, Medium ve GitHub Trending kaynaklarından sürekli makale toplanması
- 🤖 **AI Puanlama** — GPT-4o-mini ile her makaleye 1–10 arası alaka düzeyi puanı atanması
- 🇹🇷 **Türkçe Özet** — Puanı 6.0 üzeri makaleler için 3 maddelik Türkçe özet üretimi
- 🧠 **Vektör Arama** — ChromaDB + OpenAI Embeddings ile anlamsal arama (keyword değil, anlam bazlı)
- 📱 **Telegram Entegrasyonu** — Puanı 7.5+ olan makaleler otomatik olarak Telegram'a gönderilir; `/run` komutu ile pipeline tetiklenebilir
- 📊 **Analytics Dashboard** — Token harcaması, günlük makale alımı ve kategori dağılımı takibi

---

## 🏗️ Sistem Mimarisi

```
APScheduler (her 4 saatte bir)
    │
    ├─► Scout Ajanı        (ArXiv · Medium · GitHub Trending)
    │       ↓ URL tekrar kontrolü (PostgreSQL)
    │       ↓ Metin temizleme
    │
    ├─► Analizör Ajanı     (4 Kademeli Token Protokolü)
    │       T0: Anahtar kelime filtresi  → 0 token
    │       T1: GPT-4o-mini puanlama    → ~150 token
    │       T2: Türkçe özet             → ~300 token (puan ≥ 6.0)
    │       T3: Vektör embedding        → ~50 token  (puan ≥ 6.0)
    │       ↓ PostgreSQL + ChromaDB'ye kayıt
    │
    └─► Dağıtıcı Ajanı     (Telegram MarkdownV2, puan ≥ 7.5)
            ↓ is_dispatched = True olarak işaretleme

FastAPI REST API  ←→  Next.js 14 Dashboard
    /api/articles          Makale akışı + filtreler
    /api/search            Vektörel anlamsal arama
    /api/stats             Analitik ve token harcaması
    /api/run               Manuel pipeline tetikleme
    /api/telegram/webhook  Telegram webhook (gelen komutlar)
```

---

## 💰 Token Optimizasyonu

Sistem, API maliyetlerini minimize etmek için katmanlı bir protokol kullanır:

| Kademe | Koşul | İşlem | Token Maliyeti |
|--------|-------|-------|----------------|
| **T0** | Metinde AI anahtar kelimesi yok | Anında elenme | **0** |
| **T1** | T0'ı geçti | GPT-4o-mini alaka puanı | ~150 |
| **T2** | Puan ≥ 6.0 | Türkçe 3 madde özet | ~300 |
| **T3** | Puan ≥ 6.0 | text-embedding-3-small | ~50 |

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.11+
- Node.js 18+
- Supabase hesabı (ücretsiz tier yeterli)
- OpenAI API anahtarı
- Telegram Bot Token + Chat ID

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/turanakcann/ai-radar-internship-project.git
cd ai-radar-internship-project
```

### 2. Ortam Değişkenlerini Yapılandırın

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

`.env` dosyasını açın ve `<YOUR_...>` ile işaretlenmiş tüm değerleri doldurun.

### 3. Python Bağımlılıklarını Kurun

```bash
# Sanal ortam oluşturun
python -m venv venv

# Aktif edin (Windows)
.\venv\Scripts\Activate.ps1

# Aktif edin (macOS/Linux)
source venv/bin/activate

# Bağımlılıkları kurun
pip install poetry
poetry install
```

### 4. Backend'i Başlatın

```bash
# FastAPI sunucusu — http://localhost:8000
uvicorn api.main:app --reload --port 8000
```

### 5. Frontend'i Başlatın

Yeni bir terminal açın:

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 6. Uygulamaya Erişin

| Servis | URL |
|--------|-----|
| 🌐 Dashboard | http://localhost:3000 |
| 📡 API Docs (Swagger) | http://localhost:8000/api/docs |
| 💊 Health Check | http://localhost:8000/api/health |

---

## 🤖 Telegram Bot Kurulumu

### Bot Token Alma

1. Telegram'da [@BotFather](https://t.me/BotFather)'a gidin
2. `/newbot` komutunu gönderin ve yönergeleri takip edin
3. Aldığınız token'ı `.env` dosyasına `TELEGRAM_BOT_TOKEN` olarak ekleyin

### Chat ID Bulma

1. Botu grubunuza/kanalınıza **Yönetici** olarak ekleyin
2. Kanala herhangi bir mesaj gönderin
3. Tarayıcıda şu adresi açın:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. JSON yanıtındaki `"chat":{"id": -100xxxxxxxxxx}` değerini kopyalayın
5. `.env` dosyasına `TELEGRAM_CHAT_ID` olarak yapıştırın

### Webhook Kurulumu (Ngrok ile)

```bash
# Terminal 1: API sunucusunu başlatın
uvicorn api.main:app --reload

# Terminal 2: Ngrok tünelini açın
.\ngrok.exe http 8000

# Terminal 3: Webhook'u kaydedin
.\venv\Scripts\python setup_webhook.py
# → Public URL'yi girin (örnek: https://abc123.ngrok-free.app)
```

Artık Telegram'dan `/run` komutu göndererek pipeline'ı tetikleyebilirsiniz.

---

## 🌐 API Referansı

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| `GET` | `/api/articles` | Sayfalandırılmış makale akışı (kaynak/kategori/puan filtresi) |
| `GET` | `/api/articles/{id}` | Tek makale detayı |
| `POST` | `/api/search` | Vektörel anlamsal arama |
| `GET` | `/api/stats` | Pipeline analitikleri ve token istatistikleri |
| `POST` | `/api/run` | Pipeline'ı manuel olarak tetikleme |
| `GET` | `/api/run/status` | Pipeline çalışıyor mu? |
| `GET` | `/api/health` | Sağlık kontrolü |
| `POST` | `/api/telegram/webhook` | Telegram webhook (gelen komutlar) |

---

## 📁 Proje Yapısı

```
ai-radar-internship-project/
├── api/                    # FastAPI uygulaması
│   ├── main.py             # Uygulama fabrikası, CORS, router kaydı
│   └── routes/
│       ├── articles.py     # Makale CRUD endpoint'leri
│       ├── search.py       # Vektörel arama endpoint'i
│       ├── stats.py        # Analitik endpoint'i
│       ├── trigger.py      # Pipeline tetikleme endpoint'i
│       └── telegram.py     # Telegram webhook (gelen /run komutu)
├── agents/                 # Çok-ajan sistemi
│   └── orchestrator.py     # Scout → Analizör → Dağıtıcı koordinasyonu
├── connectors/             # Veri kaynağı bağlayıcıları (ArXiv, Medium, GitHub)
├── core/                   # Paylaşılan altyapı
│   ├── config.py           # Pydantic Settings
│   ├── database.py         # SQLAlchemy async engine
│   ├── models.py           # ORM modelleri
│   ├── schemas.py          # Pydantic şemaları
│   ├── chromadb_client.py  # ChromaDB vektör veritabanı istemcisi
│   └── telegram.py         # Telegram Bot API yardımcısı (HTML parse_mode)
├── frontend/               # Next.js 14 dashboard
│   ├── app/
│   │   ├── page.tsx        # Ana sayfa — makale akışı
│   │   ├── search/         # Anlamsal arama sayfası
│   │   └── analytics/      # Pipeline analitik sayfası
│   └── components/
│       ├── ArticleCard.tsx  # Makale kartı bileşeni
│       ├── CategoryFilter.tsx
│       ├── Navbar.tsx
│       └── SearchBar.tsx
├── pictures/               # Proje ekran görüntüleri
├── .env.example            # Ortam değişkenleri şablonu
├── setup_webhook.py        # Telegram webhook kayıt yardımcısı
├── docker-compose.yml      # Docker Compose yapılandırması
└── pyproject.toml          # Python bağımlılıkları (Poetry)
```

---

## 🔧 Ortam Değişkenleri

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `DATABASE_URL` | ✅ | PostgreSQL asyncpg bağlantı URL'si |
| `SUPABASE_URL` | ✅ | Supabase proje URL'si |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase tam yetkili anahtar (backend) |
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | Supabase URL'si (frontend) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabase anonim anahtarı (frontend) |
| `OPENAI_API_KEY` | ✅ | OpenAI API anahtarı |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot API token'ı |
| `TELEGRAM_CHAT_ID` | ✅ | Hedef kanal/grup ID'si |
| `ANTHROPIC_API_KEY` | ☐ | Anthropic yedek LLM (isteğe bağlı) |
| `RELEVANCE_THRESHOLD_SUMMARY` | ☐ | Özet eşiği (varsayılan: 6.0) |
| `RELEVANCE_THRESHOLD_DISPATCH` | ☐ | Telegram gönderme eşiği (varsayılan: 7.5) |
| `SCHEDULE_INTERVAL_HOURS` | ☐ | Zamanlayıcı aralığı (varsayılan: 4 saat) |

---

## 🧪 Testleri Çalıştırma

```bash
poetry run pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 🐳 Docker ile Dağıtım

```bash
docker compose up --build
```

Servisler:

| Servis | Port | Açıklama |
|--------|------|----------|
| `api` | 8000 | FastAPI backend |
| `postgres` | 5432 | PostgreSQL 16 |
| `chromadb` | 8001 | ChromaDB vektör veritabanı |
| `redis` | 6379 | Redis önbellek |
| `scheduler` | — | APScheduler pipeline orchestrator |

---

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır.

---

<div align="center">

❤️ ile **Davision AI** tarafından geliştirilmiştir — Otonom Yapay Zeka İstihbarat Platformu

</div>


[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange.svg)](https://trychroma.com)

---

## Architecture

```
APScheduler (every 4h)
    │
    ├─► Scout Agent        (ArXiv · Medium · GitHub Trending)
    │       ↓ URL dedup against PostgreSQL
    │       ↓ Text cleaning
    │
    ├─► Analyzer Agent     (4-Tier Token Protocol)
    │       T0: Keyword filter     → 0 tokens
    │       T1: GPT-4o-mini score  → ~150 tokens
    │       T2: Turkish summary    → ~300 tokens (if score ≥ 6.0)
    │       T3: Embedding          → ~50 tokens  (if score ≥ 6.0)
    │       ↓ PostgreSQL + ChromaDB
    │
    └─► Dispatcher Agent   (Telegram MarkdownV2 alerts, score ≥ 7.5)
            ↓ mark is_dispatched = True

FastAPI REST API  ←→  Next.js 14 Dashboard
    /api/articles      Feed + filters
    /api/search        Semantic vector search
    /api/stats         Analytics & token spend
    /api/run           Manual pipeline trigger
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- OpenAI API key
- Telegram Bot Token + Chat ID

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Infrastructure

```bash
docker compose up -d postgres chromadb redis
```

### 3. Install Python Dependencies

```bash
pip install poetry
poetry install
```

### 4. Start the Backend

```bash
# FastAPI Server
uvicorn api.main:app --reload --port 8000

# Scheduler (separate terminal)
python -m agents.orchestrator
```

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Manual Pipeline Trigger

```bash
curl -X POST http://localhost:8000/api/run
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL asyncpg URL |
| `OPENAI_API_KEY` | ✅ | OpenAI API key for scoring + embeddings |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot API token |
| `TELEGRAM_CHAT_ID` | ✅ | Target chat/channel ID |
| `ANTHROPIC_API_KEY` | ☐ | Fallback LLM (optional) |
| `SCHEDULE_INTERVAL_HOURS` | ☐ | Cron interval (default: 4) |
| `RELEVANCE_THRESHOLD_SUMMARY` | ☐ | Min score for Turkish summary (default: 6.0) |
| `RELEVANCE_THRESHOLD_DISPATCH` | ☐ | Min score for Telegram alert (default: 7.5) |

## Token Optimization

The Analyzer uses a strict 4-tier protocol to minimize API costs:

| Tier | Condition | Action | Token Cost |
|------|-----------|--------|-----------|
| T0 | No AI keywords in text | Discard immediately | **0** |
| T1 | Passes T0 | GPT-4o-mini relevance score | ~150 |
| T2 | Score ≥ 6.0 | Turkish 3-bullet summary | ~300 |
| T3 | Score ≥ 6.0 | text-embedding-3-small | ~50 |

## Running Tests

```bash
poetry run pytest tests/ -v --cov=. --cov-report=term-missing
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | Paginated article feed with filters |
| GET | `/api/articles/{id}` | Single article detail |
| POST | `/api/search` | Semantic vector search |
| GET | `/api/stats` | Pipeline analytics |
| POST | `/api/run` | Trigger pipeline manually |
| GET | `/api/health` | Health check |

## Frontend Pages

| Page | URL | Description |
|------|-----|-------------|
| Feed | `/` | Article feed with source/category/score filters |
| Search | `/search` | Semantic vector search with similarity scores |
| Analytics | `/analytics` | Token spend, ingestion trends, category breakdown |

## Docker Deployment

```bash
docker compose up --build
```

Services:
- `postgres`: PostgreSQL 16 on port 5432
- `chromadb`: ChromaDB on port 8001
- `redis`: Redis 7 on port 6379
- `api`: FastAPI on port 8000
- `scheduler`: APScheduler orchestrator

---

Built with ❤️ by **Davision AI** — Autonomous Intelligence Platform
