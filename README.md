# Saudagar.ai (Sistem Asisten Usaha Dagang Pintar)

Ekosistem **asisten virtual + dashboard analitik** untuk UMKM Indonesia. Alih-alih
memaksa pedagang mempelajari aplikasi kasir yang rumit, Saudagar.ai bertindak
sebagai **"karyawan digital"** yang bisa diajak mengobrol - mencatat keuangan &
stok dari bahasa sehari-hari, melayani pelanggan otomatis, dan menerjemahkan
data menjadi insight yang mudah dipahami.

<p align="center"><em>Next.js · FastAPI · LangChain · Google Gemini (RAG + MCP-style tools)</em></p>

---

## Fitur (MVP)

| Fitur                               | Deskripsi                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Pencatatan via Natural Language** | Kirim "laku 15 porsi nasi goreng, beli telur 2 kg 55 ribu" → AI mengekstrak intent, mengategorikan, dan memperbarui database real-time. |
| **Auto-CS & AI Sales Engine**       | AI menjawab calon pembeli, mengecek stok dari katalog, dan melakukan up-selling relevan.                                                |
| **Narasi Analitik & Rekomendasi**   | Dashboard membaca data dan menuliskannya sebagai insight sederhana + saran bisnis.                                                      |
| **Katalog Multi-Bahasa**            | Masukkan nama produk → AI membuat copywriting menarik dalam banyak bahasa, siap tempel ke marketplace.                                  |

## Arsitektur

```
saudagar-ai/
├── backend/     FastAPI + LangChain + Gemini  (RAG grounding + MCP-style tools)
│               → REST API di http://localhost:8000
└── frontend/    Next.js 16 + Tailwind v4      (dashboard, desain ala Wise - lihat DESIGN.md)
                → Web app di http://localhost:3000
```

- **RAG**: setiap jawaban AI dibumikan pada katalog & aturan toko spesifik agar tidak berhalusinasi.
- **MCP-style tools**: LLM hanya boleh mengubah data lewat sekumpulan tool teraudit (catat penjualan, ubah stok, dst).
- **Mode demo tanpa API key**: seluruh alur berjalan dengan respons rule-based deterministik. Isi `GEMINI_API_KEY` untuk mengaktifkan AI penuh.

## Menjalankan

### 1. Backend (FastAPI)

```bash
cd backend
venv\Scripts\Activate.ps1          # venv sudah tersedia (Windows PowerShell)
pip install -r requirements.txt
cp .env.example .env               # isi GEMINI_API_KEY (opsional)
uvicorn app.main:app --reload --port 8000
```

Docs API: http://localhost:8000/docs · database SQLite otomatis dibuat & diisi data demo (Warung Bu Sari).

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local         # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

Buka http://localhost:3000.

## Konfigurasi environment

| File                    | Kunci penting                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| `backend/.env.example`  | `GEMINI_API_KEY`, `GEMINI_MODEL` (default `gemini-2.5-flash`), `DATABASE_URL`, `CORS_ORIGINS` |
| `frontend/.env.example` | `NEXT_PUBLIC_API_BASE_URL`                                                                    |
