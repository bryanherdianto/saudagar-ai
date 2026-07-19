# Saudagar.ai (Sistem Asisten Usaha Dagang Pintar)

<img width="1200" height="400" alt="banner_saudagarai" src="https://github.com/user-attachments/assets/b4279e11-7e46-49c4-b16d-ccea8901d242" />


<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Express.js-000000?style=for-the-badge&logo=express&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Clerk-6C47FF?style=for-the-badge&logo=clerk&logoColor=white" />
  <img src="https://img.shields.io/badge/Framer_Motion-0055FF?style=for-the-badge&logo=framer&logoColor=white" />
  <img src="https://img.shields.io/badge/Puppeteer-40B5A4?style=for-the-badge&logo=puppeteer&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" />
</p>

---
## Overivew

Ekosistem **asisten virtual + dashboard analitik** untuk UMKM Indonesia. Alih-alih
memaksa pedagang mempelajari aplikasi kasir yang rumit, Saudagar.ai bertindak
sebagai **"karyawan digital"** yang bisa diajak mengobrol - mencatat keuangan &
stok dari bahasa sehari-hari, melayani pelanggan otomatis, dan menerjemahkan
data menjadi insight yang mudah dipahami.


## Fitur (MVP)

| Fitur                               | Deskripsi                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Pencatatan via Natural Language** | Kirim "laku 15 porsi nasi goreng, beli telur 2 kg 55 ribu" → AI mengekstrak intent, mengategorikan, dan memperbarui database real-time. |                                        |
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
