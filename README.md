# Saudagar.ai (Sistem Asisten Usaha Dagang Pintar)

<img alt="banner_saudagarai" src="https://github.com/user-attachments/assets/b4279e11-7e46-49c4-b16d-ccea8901d242" />

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/Clerk-6C47FF?style=for-the-badge&logo=clerk&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" />
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" />
</p>

## Overview

Ekosistem **asisten virtual + dashboard analitik** untuk UMKM Indonesia. Alih-alih memaksa pedagang mempelajari aplikasi kasir yang rumit, Saudagar.ai bertindak sebagai **"karyawan digital"** yang bisa diajak mengobrol. Dia bisa mencatat keuangan dan stok dari bahasa sehari-hari, melayani pelanggan otomatis, dan menerjemahkan data menjadi insight yang mudah dipahami.

## Fitur (MVP)

| Fitur                               | Deskripsi                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Pencatatan via Natural Language** | Kirim "laku 15 porsi nasi goreng, beli telur 2 kg 55 ribu" → AI mengekstrak intent, mengategorikan, dan memperbarui database real-time. |
| **Narasi Analitik & Rekomendasi**   | Dashboard membaca data dan menuliskannya sebagai insight sederhana + saran bisnis.                                                      |
| **Katalog Multi-Bahasa**            | Masukkan nama produk → AI membuat copywriting menarik dalam banyak bahasa, siap tempel ke marketplace.                                  |
| **Integrasi Telegram**              | Hubungkan bot Telegram agar pencatatan bisa dilakukan langsung dari chat, tanpa membuka dashboard.                                      |

## Cara Menjalankan

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv                # lewati jika venv sudah ada
venv\Scripts\Activate.ps1          # Windows PowerShell (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env               # isi GEMINI_API_KEY (opsional)
uvicorn app.main:app --reload --port 8000
```

Backend server akan berjalan di http://localhost:8000.

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local         # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

Buka http://localhost:3000.

## Video Demo

[![Demo Saudagar.ai](https://img.youtube.com/vi/mYCND7qTX9I/maxresdefault.jpg)](https://youtu.be/mYCND7qTX9I)
