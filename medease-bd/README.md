# MedEase BD — Medicine Information Chatbot

AI-powered medicine chatbot for Bangladesh, optimised for **Ryzen 4500U + 16 GB RAM** (CPU-only).

## Hardware Optimisations Applied

| Setting | Value | Reason |
|---------|-------|--------|
| `n_threads` | 5 | 5 of 6 Ryzen cores; 1 left for OS |
| `n_batch` | 32 | Ryzen handles 32-token batches well |
| `n_ctx` | 512 | Enough for RAG; keeps RAM low |
| `f16_kv` | false | CPU doesn't benefit from float16 KV |
| `use_mlock` | false | Avoids memory pressure under Docker |
| OpenBLAS | enabled | Ryzen AVX2 → faster matrix math |
| Postgres shared_buffers | 512 MB | Right-sized for 16 GB host |
| Docker memory limits | set per service | Prevents OOM under full load |

**Expected RAM usage (all containers running):**

| Service | RAM |
|---------|-----|
| PostgreSQL | ~1.5 GB |
| Redis | ~256 MB |
| Backend + LLM loaded | ~3–3.5 GB |
| Frontend | ~500 MB |
| System / OS | ~2 GB |
| **Total** | **~8–9 GB** (7 GB headroom on 16 GB) |

**Expected response time:** 4–8 seconds per query on Ryzen 4500U.

---

## Quick Start

### 1. Prerequisites
- Docker Desktop (WSL 2 backend, ≥ 12 GB memory limit)
- Git

### 2. Clone
```bash
git clone https://github.com/Simanto023/medease-bd.git
cd medease-bd
```

### 3. Download the GGUF model
```bash
mkdir -p backend/app/models

# Download Qwen 2.5 1.5B Q4_0 (~1 GB)
# From: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
# File: qwen2.5-1.5b-instruct-q4_0.gguf
# Place it at: backend/app/models/qwen2.5-1.5b-instruct.Q4_0.gguf
```

### 4. Add your medicine CSV
Place your CSV at `data_init/data/medicines.csv`  
Required columns: `brand_name`, `generic_name`, `company`, `strength`, `form`, `price_bdt`

### 5. Start
```bash
docker-compose up -d
```

- Frontend: http://localhost:3000  
- API docs: http://localhost:8000/docs

---

## API Endpoints

### Chat
```
POST /api/v1/chat
{
  "query": "What is Napa?",
  "company": "Beximco",   // optional
  "language": "en"        // "en" or "bn"
}
```

### Search
```
GET /api/v1/medicines/search?query=napa&limit=10
GET /api/v1/medicines/company/Beximco
```

---

## Troubleshooting

**Model not loading:** Check `backend/app/models/` contains the `.gguf` file.  
**Out of memory:** Open Docker Desktop → Settings → Resources → set Memory ≥ 12 GB.  
**Slow first response:** Normal — model loads on first request (~10 seconds).

---

> ⚠️ MedEase BD provides information for educational purposes only. Always consult healthcare professionals.
