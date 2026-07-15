"""The conversational assistant agent.

`run_assistant` runs a native function-calling loop: Gemini decides which
MCP-style tools to call, we execute them against the live database, feed the
results back, and repeat until the model produces a final answer.

When no API key is configured it degrades to a lightweight rule-based parser
so the "record a sale by chatting" flow still works in a demo.

`store_id` is threaded through every tool call so two stores' data is never
mixed when the AI is acting.
"""

from __future__ import annotations

import re

from sqlmodel import Session, select

from app import services
from app.ai.llm import get_llm
from app.ai.rag import retrieve_context
from app.ai.tools import build_tools
from app.models import Product
from app.schemas import ChatMessage

SYSTEM_PROMPT = """Kamu adalah "Saudagar.ai", asisten digital untuk pemilik UMKM di Indonesia.
Kamu berperan seperti karyawan digital yang ramah, ringkas, dan cekatan.

Tugasmu:
- Mencatat pemasukan/penjualan dan pengeluaran dari bahasa sehari-hari.
- Mengelola dan mengecek stok produk.
- Menjawab pertanyaan bisnis berdasarkan data toko yang diberikan.

Aturan:
- SELALU gunakan tools yang tersedia untuk mencatat transaksi atau mengubah stok — jangan hanya mengklaim sudah dicatat.
- Rujuk pada KONTEKS TOKO di bawah; jangan mengarang produk atau harga yang tidak ada.
- Jika informasi kurang (mis. jumlah tidak jelas), tanyakan singkat.
- Jawab dalam Bahasa Indonesia yang santai dan singkat. Gunakan format Rupiah.
"""

MAX_TOOL_ITERATIONS = 5


def run_assistant(
    session: Session,
    store_id: int,
    message: str,
    history: list[ChatMessage] | None = None,
) -> tuple[str, list[str], bool]:
    """Return (reply, actions_taken, ai_enabled)."""
    history = history or []
    llm = get_llm()
    if llm is None:
        reply, actions = _rule_based_assistant(session, store_id, message)
        return reply, actions, False

    from langchain_core.messages import (
        AIMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage,
    )

    tools = build_tools(session, store_id)
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)

    context = retrieve_context(session, store_id, message)
    # Gemini only accepts a single system message (at position 0), so combine
    # the base prompt and the retrieved store context into one.
    messages: list = [
        SystemMessage(content=f"{SYSTEM_PROMPT}\n\nKONTEKS TOKO (hasil RAG):\n{context}"),
    ]
    for m in history[-8:]:
        if m.role == "user":
            messages.append(HumanMessage(content=m.content))
        else:
            messages.append(AIMessage(content=m.content))
    messages.append(HumanMessage(content=message))

    actions: list[str] = []
    for _ in range(MAX_TOOL_ITERATIONS):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        tool_calls = getattr(ai_msg, "tool_calls", None) or []
        if not tool_calls:
            return (ai_msg.content or "").strip(), actions, True

        for call in tool_calls:
            tool = tools_by_name.get(call["name"])
            if tool is None:
                result = f"Tool '{call['name']}' tidak tersedia."
            else:
                try:
                    result = tool.invoke(call["args"])
                except Exception as exc:  # surface tool errors back to the model
                    result = f"Gagal menjalankan tool: {exc}"
            actions.append(result)
            # `name` is required: Gemini maps each ToolMessage to a
            # function_response and rejects the request if its name is empty.
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call["id"],
                    name=call["name"],
                )
            )

    # Ran out of iterations — return a best-effort summary of what we did.
    fallback = "Beberapa aksi sudah dijalankan:\n" + "\n".join(f"- {a}" for a in actions)
    return fallback, actions, True


# --------------------------------------------------------------------------
# Rule-based fallback (mock mode, no API key)
# --------------------------------------------------------------------------
_NUMBER_WORDS = {
    "nol": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
    "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9, "sepuluh": 10,
}
_INCOME_KEYWORDS = ("laku", "terjual", "jual", "penjualan", "laris")
_EXPENSE_KEYWORDS = ("beli", "belanja", "bayar", "pengeluaran", "modal")


def _parse_amount(text: str) -> float | None:
    """Parse a rupiah amount, but only when a price cue is present.

    Matches things like '55 ribu', '1.2 juta', 'harganya 20000'. A bare number
    such as the '10' in 'laku 10 es teh manis' is treated as a quantity
    elsewhere, not an amount, so we require a scale suffix or a price keyword.
    """
    # 1) number followed by a scale word (ribu/juta/…)
    scaled = re.search(r"(\d+(?:[.,]\d+)?)\s*(ribu|rb|k|juta|jt)\b", text)
    if scaled:
        value = float(scaled.group(1).replace(",", "."))
        scale = {"ribu": 1e3, "rb": 1e3, "k": 1e3, "juta": 1e6, "jt": 1e6}[scaled.group(2)]
        return value * scale
    # 2) explicit price keyword followed by a plain number (>= 100 to skip qty)
    priced = re.search(r"(?:harga\w*|seharga|rp\.?\s*)\s*(\d{3,}(?:[.,]\d+)?)", text)
    if priced:
        return float(priced.group(1).replace(".", "").replace(",", "."))
    return None


def _rule_based_assistant(
    session: Session, store_id: int, message: str
) -> tuple[str, list[str]]:
    """A deterministic parser used when Gemini is not configured."""
    text = message.lower()
    actions: list[str] = []

    # Stock check intent — try to match a known product name in the message.
    if any(w in text for w in ("stok", "sisa", "ada berapa")):
        for product in session.exec(
            select(Product).where(Product.store_id == store_id)
        ).all():
            if product.name.lower() in text:
                status = "menipis" if product.stock <= product.low_stock_threshold else "aman"
                return (
                    f"Stok {product.name} tinggal {product.stock:g} {product.unit} ({status}).",
                    actions,
                )
        return ("Sebutkan nama produk yang ingin dicek stoknya, ya.", actions)

    amount = _parse_amount(text)
    qty_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(porsi|gelas|kg|kilo|botol|bungkus|pcs|buah|ekor)", text)
    if qty_match:
        quantity = float(qty_match.group(1).replace(",", "."))
        unit = qty_match.group(2)
    else:
        # No explicit unit — treat the first bare number (not part of a rupiah
        # amount) as the quantity, e.g. "laku 10 es teh manis".
        without_amount = re.sub(r"\d+(?:[.,]\d+)?\s*(?:ribu|rb|k|juta|jt)\b", " ", text)
        bare = re.search(r"\b(\d+(?:[.,]\d+)?)\b", without_amount)
        quantity = float(bare.group(1).replace(",", ".")) if bare else 1.0
        unit = ""

    # Guess product name: strip numbers/units/keywords.
    cleaned = re.sub(r"\d+[.,]?\d*", "", text)
    for kw in _INCOME_KEYWORDS + _EXPENSE_KEYWORDS + ("porsi", "gelas", "botol", "bungkus", "kg", "kilo", "ribu", "rb", "juta", "harganya", "harga", "seharga", "terus", "hari", "ini", "tadi"):
        cleaned = cleaned.replace(kw, " ")
    product_guess = " ".join(cleaned.split()).strip(" .,")

    if any(w in text for w in _EXPENSE_KEYWORDS):
        tx = services.record_expense(
            session, store_id, amount or 0.0, product_name=product_guess,
            quantity=quantity, unit=unit, source="assistant",
        )
        msg = f"Oke, dicatat pengeluaran Rp{tx.amount:,.0f}"
        msg += f" untuk {quantity:g} {unit} {product_guess}." if product_guess else "."
        actions.append(msg)
        return msg + " (mode demo tanpa API key)", actions

    if any(w in text for w in _INCOME_KEYWORDS) or qty_match:
        tx = services.record_sale(
            session, store_id, product_guess, quantity, amount, unit, source="assistant",
        )
        msg = f"Sip! Dicatat penjualan {quantity:g} {tx.unit} {tx.product_name} senilai Rp{tx.amount:,.0f}."
        actions.append(msg)
        return msg + " (mode demo tanpa API key)", actions

    return (
        "Saya asisten Saudagar.ai (mode demo). Coba tulis seperti: "
        "'laku 15 porsi nasi goreng' atau 'beli telur 2 kg harganya 55 ribu'. "
        "Untuk fitur AI penuh, isi GEMINI_API_KEY di file .env.",
        actions,
    )