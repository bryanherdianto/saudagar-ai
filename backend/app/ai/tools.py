"""MCP-style tools that give the AI agent real-time access to store data.

Following the Model Context Protocol philosophy, the LLM never touches the
database directly - it can only act through this small, audited set of tools.
Each tool is bound to a live SQLModel `Session` and a `store_id` via a
closure and returns a plain string the model can read back.

We build them with LangChain's `StructuredTool` so they can be passed to
`ChatGoogleGenerativeAI.bind_tools()` for native function calling.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from sqlmodel import Session

from app import services


# --- Tool argument schemas ---
class RecordSaleArgs(BaseModel):
    product_name: str = Field(description="Nama produk yang terjual")
    quantity: float = Field(description="Jumlah unit yang terjual")
    amount: float | None = Field(
        default=None,
        description="Total nilai penjualan dalam Rupiah. Kosongkan agar dihitung dari harga katalog.",
    )
    unit: str = Field(default="", description="Satuan, mis. porsi, kg, botol")


class RecordExpenseArgs(BaseModel):
    amount: float = Field(description="Total pengeluaran dalam Rupiah")
    category: str = Field(default="pembelian stok", description="Kategori pengeluaran")
    product_name: str = Field(default="", description="Produk yang dibeli, jika ada")
    quantity: float = Field(default=0.0, description="Jumlah unit yang dibeli")
    unit: str = Field(default="", description="Satuan pembelian")
    description: str = Field(default="", description="Catatan tambahan")


class CheckStockArgs(BaseModel):
    product_name: str = Field(description="Nama produk yang dicek stoknya")


class SetStockArgs(BaseModel):
    product_name: str = Field(description="Nama produk")
    stock: float = Field(description="Nilai stok baru")


class AddProductArgs(BaseModel):
    name: str = Field(description="Nama produk baru")
    price: float = Field(default=0.0, description="Harga jual per unit")
    stock: float = Field(default=0.0, description="Stok awal")
    unit: str = Field(default="pcs", description="Satuan")
    category: str = Field(default="", description="Kategori produk")


class SummaryArgs(BaseModel):
    days: int = Field(default=7, description="Rentang hari untuk ringkasan penjualan")


def build_tools(session: Session, store_id: int, source: str = "assistant") -> list[Any]:
    """Create the tool set bound to a database session and a store scope.

    `source` is stamped on any transaction these tools record, so the channel
    that triggered the AI (dashboard vs. telegram) is preserved for auditing.
    """
    from langchain_core.tools import StructuredTool

    def _record_sale(product_name: str, quantity: float, amount: float | None = None, unit: str = "") -> str:
        tx = services.record_sale(
            session, store_id, product_name, quantity, amount, unit, source=source
        )
        return (
            f"Tercatat penjualan {tx.quantity:g} {tx.unit} {tx.product_name} "
            f"senilai Rp{tx.amount:,.0f}."
        )

    def _record_expense(
        amount: float,
        category: str = "pembelian stok",
        product_name: str = "",
        quantity: float = 0.0,
        unit: str = "",
        description: str = "",
    ) -> str:
        tx = services.record_expense(
            session, store_id, amount, category, description, product_name,
            quantity, unit, source=source,
        )
        extra = f" untuk {tx.quantity:g} {tx.unit} {tx.product_name}" if tx.product_name else ""
        return f"Tercatat pengeluaran '{tx.category}'{extra} senilai Rp{tx.amount:,.0f}."

    def _check_stock(product_name: str) -> str:
        product = services.find_product(session, product_name, store_id)
        if not product:
            return f"Produk '{product_name}' tidak ditemukan di katalog."
        status = "MENIPIS" if product.stock <= product.low_stock_threshold else "aman"
        return (
            f"Stok {product.name}: {product.stock:g} {product.unit} ({status}). "
            f"Harga jual Rp{product.price:,.0f}."
        )

    def _set_stock(product_name: str, stock: float) -> str:
        product = services.set_stock(session, store_id, product_name, stock)
        if not product:
            return f"Produk '{product_name}' tidak ditemukan."
        return f"Stok {product.name} diperbarui menjadi {product.stock:g} {product.unit}."

    def _add_product(name: str, price: float = 0.0, stock: float = 0.0, unit: str = "pcs", category: str = "") -> str:
        product = services.upsert_product(
            session, store_id, name, price, stock, unit, category
        )
        return (
            f"Produk '{product.name}' disimpan: harga Rp{product.price:,.0f}/{product.unit}, "
            f"stok {product.stock:g}."
        )

    def _sales_summary(days: int = 7) -> str:
        s = services.sales_summary(session, store_id, days)
        top = ", ".join(f"{p['name']} (Rp{p['revenue']:,.0f})" for p in s["top_products"]) or "-"
        low = ", ".join(f"{p['name']} ({p['stock']:g})" for p in s["low_stock"]) or "tidak ada"
        return (
            f"Ringkasan {days} hari: pemasukan Rp{s['income']:,.0f}, "
            f"pengeluaran Rp{s['expense']:,.0f}, laba Rp{s['profit']:,.0f}. "
            f"Produk terlaris: {top}. Stok menipis: {low}."
        )

    return [
        StructuredTool.from_function(
            _record_sale,
            name="record_sale",
            description="Catat transaksi penjualan/pemasukan dan kurangi stok produk.",
            args_schema=RecordSaleArgs,
        ),
        StructuredTool.from_function(
            _record_expense,
            name="record_expense",
            description="Catat pengeluaran (mis. pembelian stok, biaya operasional).",
            args_schema=RecordExpenseArgs,
        ),
        StructuredTool.from_function(
            _check_stock,
            name="check_stock",
            description="Cek ketersediaan dan harga sebuah produk di katalog.",
            args_schema=CheckStockArgs,
        ),
        StructuredTool.from_function(
            _set_stock,
            name="set_stock",
            description="Setel/perbarui jumlah stok sebuah produk ke nilai tertentu.",
            args_schema=SetStockArgs,
        ),
        StructuredTool.from_function(
            _add_product,
            name="add_product",
            description="Tambah atau perbarui produk di katalog toko.",
            args_schema=AddProductArgs,
        ),
        StructuredTool.from_function(
            _sales_summary,
            name="get_sales_summary",
            description="Ambil ringkasan penjualan, laba, produk terlaris, dan stok menipis.",
            args_schema=SummaryArgs,
        ),
    ]