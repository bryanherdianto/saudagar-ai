"""AI narrative generators for the dashboard: insights, catalog, and CS.

Each function returns a structured result and falls back to a deterministic
template when Gemini is not configured.
"""

from __future__ import annotations

import json

from sqlmodel import Session

from app.ai.llm import get_llm
from app.ai.rag import retrieve_context
from app.schemas import CatalogItem, ChatMessage
from app.services import sales_summary

LANGUAGE_NAMES = {
    "id": "Bahasa Indonesia",
    "en": "English",
    "ms": "Bahasa Melayu",
    "zh": "中文 (Mandarin)",
    "ja": "日本語",
    "ar": "العربية",
}


def _invoke_text(prompt: str) -> str | None:
    llm = get_llm()
    if llm is None:
        return None
    from langchain_core.messages import HumanMessage

    resp = llm.invoke([HumanMessage(content=prompt)])
    return (resp.content or "").strip()


# --------------------------------------------------------------------------
# Dashboard insight narrative
# --------------------------------------------------------------------------
def generate_insights(session: Session, store_id: int, days: int = 7) -> dict:
    metrics = sales_summary(session, store_id, days)
    llm = get_llm()

    if llm is None:
        return _fallback_insights(metrics)

    from langchain_core.messages import HumanMessage, SystemMessage

    prompt = (
        "Kamu analis bisnis untuk UMKM. Berdasarkan metrik JSON berikut, buat insight "
        "singkat dalam Bahasa Indonesia yang mudah dipahami pemilik warung (non-teknis).\n\n"
        f"METRIK ({days} hari terakhir):\n{json.dumps(metrics, ensure_ascii=False)}\n\n"
        "Balas HANYA JSON valid dengan bentuk:\n"
        '{"headline": "...", "narrative": "2-3 kalimat", '
        '"recommendations": ["saran 1", "saran 2", "saran 3"]}'
    )
    try:
        resp = llm.invoke(
            [
                SystemMessage(content="Kamu menjawab hanya dengan JSON valid tanpa markdown."),
                HumanMessage(content=prompt),
            ]
        )
        data = _extract_json(resp.content or "")
        return {
            "headline": data.get("headline", "Ringkasan minggu ini"),
            "narrative": data.get("narrative", ""),
            "recommendations": data.get("recommendations", []),
            "metrics": metrics,
        }
    except Exception:
        return _fallback_insights(metrics)


def _fallback_insights(metrics: dict) -> dict:
    profit = metrics["profit"]
    low = metrics["low_stock"]
    top = metrics["top_products"]
    trend = "untung" if profit >= 0 else "rugi"

    recs = []
    if top:
        recs.append(f"Produk '{top[0]['name']}' paling laris — pastikan stoknya selalu tersedia.")
    if low:
        names = ", ".join(p["name"] for p in low[:3])
        recs.append(f"Segera restock: {names} sudah menipis.")
    if profit < 0:
        recs.append("Pengeluaran melebihi pemasukan — tinjau kembali biaya pembelian stok.")
    if not recs:
        recs.append("Catat lebih banyak transaksi agar insight makin akurat.")

    narrative = (
        f"Dalam {metrics['days']} hari terakhir kamu mencatat {metrics['transaction_count']} "
        f"transaksi dengan pemasukan Rp{metrics['income']:,.0f} dan pengeluaran "
        f"Rp{metrics['expense']:,.0f}, sehingga {trend} Rp{abs(profit):,.0f}."
    )
    return {
        "headline": f"Kamu {trend} Rp{abs(profit):,.0f} minggu ini",
        "narrative": narrative,
        "recommendations": recs,
        "metrics": metrics,
    }


# --------------------------------------------------------------------------
# Multi-language catalog / copywriting
# --------------------------------------------------------------------------
def generate_catalog(
    product_name: str, details: str, languages: list[str], tone: str
) -> list[CatalogItem]:
    llm = get_llm()
    if llm is None:
        return _fallback_catalog(product_name, details, languages)

    items: list[CatalogItem] = []
    for lang in languages:
        lang_name = LANGUAGE_NAMES.get(lang, lang)
        prompt = (
            f"Tuliskan copywriting produk untuk marketplace dalam {lang_name}. "
            f"Nada: {tone}. Produk: '{product_name}'. Detail tambahan: {details or '-'}.\n"
            "Balas HANYA JSON valid: {\"title\": \"judul menarik\", \"description\": \"deskripsi 2-3 kalimat\"}"
        )
        text = _invoke_text(prompt)
        try:
            data = _extract_json(text or "")
            items.append(
                CatalogItem(
                    language=lang,
                    title=data.get("title", product_name),
                    description=data.get("description", details),
                )
            )
        except Exception:
            items.append(_fallback_catalog(product_name, details, [lang])[0])
    return items


def _fallback_catalog(product_name: str, details: str, languages: list[str]) -> list[CatalogItem]:
    templates = {
        "id": (
            f"{product_name} Berkualitas — Favorit Pelanggan",
            f"{product_name} pilihan terbaik{(' , ' + details) if details else ''}. "
            "Rasa mantap, harga bersahabat, siap kirim hari ini!",
        ),
        "en": (
            f"Premium {product_name} — Customer Favorite",
            f"Enjoy our best {product_name}{(': ' + details) if details else ''}. "
            "Great quality, friendly price, ready to ship today!",
        ),
    }
    items: list[CatalogItem] = []
    for lang in languages:
        title, desc = templates.get(lang, templates["en"])
        items.append(CatalogItem(language=lang, title=title, description=desc))
    return items


# --------------------------------------------------------------------------
# Auto customer service + upsell
# --------------------------------------------------------------------------
def generate_cs_reply(
    session: Session, store_id: int, message: str, history: list[ChatMessage]
) -> tuple[str, str | None]:
    llm = get_llm()
    context = retrieve_context(session, store_id, message)

    if llm is None:
        return _fallback_cs(message, context)

    from langchain_core.messages import HumanMessage, SystemMessage

    system = (
        "Kamu customer service + sales untuk sebuah toko UMKM. Jawab calon pembeli dengan "
        "ramah, cek ketersediaan dari KONTEKS TOKO, dan lakukan up-selling yang relevan.\n"
        f"KONTEKS TOKO:\n{context}\n\n"
        "Balas HANYA JSON valid: {\"reply\": \"jawaban ramah\", \"upsell\": \"saran tambahan atau null\"}"
    )
    try:
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=message)])
        data = _extract_json(resp.content or "")
        upsell = data.get("upsell")
        if isinstance(upsell, str) and upsell.lower() in ("null", "none", ""):
            upsell = None
        return data.get("reply", ""), upsell
    except Exception:
        return _fallback_cs(message, context)


def _fallback_cs(message: str, context: str) -> tuple[str, str | None]:
    reply = (
        "Halo kak! Terima kasih sudah menghubungi kami. Produk yang kakak tanyakan "
        "tersedia ya. Boleh diinfokan mau pesan berapa? (mode demo tanpa API key)"
    )
    return reply, "Sekalian tambah minuman dingin, kak? Lagi promo nih!"


# --------------------------------------------------------------------------
def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of an LLM response, tolerating fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])
    return json.loads(text)
