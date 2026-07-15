"""Retrieval-Augmented Generation grounding.

The agent must answer using the *specific* store's catalog and rules rather
than hallucinating. This module builds a small in-memory vector store from the
active store's product catalog + store profile and exposes a
`retrieve_context` helper.

When embeddings are unavailable (mock mode) it falls back to a naive keyword
match so grounding still works without an API key.
"""

from __future__ import annotations

from sqlmodel import Session, select

from app.ai.llm import get_embeddings
from app.models import Product, Store


def _product_to_text(p: Product) -> str:
    return (
        f"Produk: {p.name} | Kategori: {p.category or '-'} | "
        f"Harga jual: {p.price:g} per {p.unit} | Modal: {p.cost:g} | "
        f"Stok saat ini: {p.stock:g} {p.unit} "
        f"(ambang stok menipis: {p.low_stock_threshold:g}). "
        f"Deskripsi: {p.description or '-'}"
    )


def _store_to_text(s: Store) -> str:
    return (
        f"Profil Toko: {s.name} | Pemilik: {s.owner_name or '-'} | "
        f"Kategori usaha: {s.category or '-'} | Mata uang: {s.currency} | "
        f"Bahasa default: {s.default_language}. Aturan/catatan toko: {s.notes or '-'}"
    )


def build_corpus(session: Session, store_id: int) -> list[str]:
    """Assemble the grounding documents for a single store."""
    docs: list[str] = []
    store = session.exec(
        select(Store).where(Store.id == store_id)
    ).first()
    if store:
        docs.append(_store_to_text(store))
    for product in session.exec(
        select(Product).where(Product.store_id == store_id)
    ).all():
        docs.append(_product_to_text(product))
    return docs


def retrieve_context(session: Session, store_id: int, query: str, k: int = 6) -> str:
    """Return the top-k most relevant grounding snippets for `query`."""
    docs = build_corpus(session, store_id)
    if not docs:
        return "Belum ada data katalog atau profil toko."

    embeddings = get_embeddings()
    if embeddings is None:
        return _keyword_fallback(docs, query, k)

    try:
        from langchain_core.vectorstores import InMemoryVectorStore

        store = InMemoryVectorStore.from_texts(docs, embedding=embeddings)
        results = store.similarity_search(query, k=min(k, len(docs)))
        return "\n".join(f"- {r.page_content}" for r in results)
    except Exception:
        # Never let retrieval failures break the request; degrade gracefully.
        return _keyword_fallback(docs, query, k)


def _keyword_fallback(docs: list[str], query: str, k: int) -> str:
    """Rank documents by simple token overlap with the query."""
    terms = {t for t in query.lower().split() if len(t) > 2}
    scored = sorted(
        docs,
        key=lambda d: sum(1 for t in terms if t in d.lower()),
        reverse=True,
    )
    return "\n".join(f"- {d}" for d in scored[:k])