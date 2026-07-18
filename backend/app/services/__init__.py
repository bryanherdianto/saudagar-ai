"""Core business operations shared by both the REST API and the AI tools.

Keeping the logic here (rather than inside route handlers or tool wrappers)
means the AI agent and the dashboard mutate data through the exact same paths.

All functions are store-scoped: callers must pass `store_id` so two merchants
never share or mutate each other's data.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import Product, Transaction


def find_product(session: Session, name: str, store_id: int) -> Product | None:
    """Case-insensitive best-effort product lookup by name, scoped to a store."""
    if not name:
        return None
    name_l = name.strip().lower()
    products = session.exec(
        select(Product).where(Product.store_id == store_id)
    ).all()
    # Exact match first, then substring either direction.
    for p in products:
        if p.name.lower() == name_l:
            return p
    for p in products:
        if name_l in p.name.lower() or p.name.lower() in name_l:
            return p
    return None


def record_sale(
    session: Session,
    store_id: int,
    product_name: str,
    quantity: float,
    amount: float | None = None,
    unit: str = "",
    description: str = "",
    source: str = "manual",
) -> Transaction:
    """Record an income transaction and decrement stock if the product exists."""
    product = find_product(session, product_name, store_id)
    resolved_unit = unit
    if product:
        if amount is None:
            amount = product.price * quantity
        product.stock = max(0.0, product.stock - quantity)
        product.updated_at = datetime.now(timezone.utc)
        resolved_unit = unit or product.unit
        session.add(product)

    tx = Transaction(
        store_id=store_id,
        kind="income",
        category="penjualan",
        description=description or f"Penjualan {product_name}".strip(),
        amount=float(amount or 0.0),
        quantity=quantity,
        unit=resolved_unit,
        product_id=product.id if product else None,
        product_name=product.name if product else product_name,
        source=source,
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


def record_expense(
    session: Session,
    store_id: int,
    amount: float,
    category: str = "pembelian stok",
    description: str = "",
    product_name: str = "",
    quantity: float = 0.0,
    unit: str = "",
    add_to_stock: bool = True,
    source: str = "manual",
) -> Transaction:
    """Record an expense; optionally increment stock for a purchased product."""
    product = find_product(session, product_name, store_id) if product_name else None
    resolved_unit = unit
    if product and add_to_stock and quantity:
        product.stock += quantity
        product.updated_at = datetime.now(timezone.utc)
        resolved_unit = unit or product.unit
        session.add(product)

    tx = Transaction(
        store_id=store_id,
        kind="expense",
        category=category,
        description=description or (f"Pembelian {product_name}".strip() if product_name else "Pengeluaran"),
        amount=float(amount),
        quantity=quantity,
        unit=resolved_unit,
        product_id=product.id if product else None,
        product_name=product.name if product else product_name,
        source=source,
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


def set_stock(session: Session, store_id: int, product_name: str, stock: float) -> Product | None:
    product = find_product(session, product_name, store_id)
    if not product:
        return None
    product.stock = max(0.0, stock)
    product.updated_at = datetime.now(timezone.utc)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def upsert_product(
    session: Session,
    store_id: int,
    name: str,
    price: float = 0.0,
    stock: float = 0.0,
    unit: str = "pcs",
    category: str = "",
    cost: float = 0.0,
    description: str = "",
    sku: str | None = None,
    low_stock_threshold: float = 5.0,
) -> Product:
    product = find_product(session, name, store_id)
    if product:
        product.price = price or product.price
        product.stock = stock if stock else product.stock
        product.unit = unit or product.unit
        product.category = category or product.category
        product.cost = cost or product.cost
        product.description = description or product.description
        if sku is not None:
            product.sku = sku
        product.low_stock_threshold = low_stock_threshold or product.low_stock_threshold
        product.updated_at = datetime.now(timezone.utc)
    else:
        product = Product(
            store_id=store_id,
            name=name,
            price=price,
            stock=stock,
            unit=unit,
            category=category,
            cost=cost,
            description=description,
            sku=sku,
            low_stock_threshold=low_stock_threshold,
        )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def low_stock_products(session: Session, store_id: int) -> list[Product]:
    return [
        p
        for p in session.exec(
            select(Product).where(Product.store_id == store_id)
        ).all()
        if p.stock <= p.low_stock_threshold
    ]


def sales_summary(session: Session, store_id: int, days: int = 7) -> dict:
    """Aggregate income/expense over the trailing `days` window, scoped to a store."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    txs = session.exec(
        select(Transaction).where(
            Transaction.store_id == store_id,
            Transaction.created_at >= since,
        )
    ).all()

    income = sum(t.amount for t in txs if t.kind == "income")
    expense = sum(t.amount for t in txs if t.kind == "expense")

    # Best-selling products by revenue in the window.
    by_product: dict[str, float] = {}
    for t in txs:
        if t.kind == "income" and t.product_name:
            by_product[t.product_name] = by_product.get(t.product_name, 0.0) + t.amount
    top = sorted(by_product.items(), key=lambda kv: kv[1], reverse=True)[:5]

    return {
        "days": days,
        "income": round(income, 2),
        "expense": round(expense, 2),
        "profit": round(income - expense, 2),
        "transaction_count": len(txs),
        "top_products": [{"name": n, "revenue": round(v, 2)} for n, v in top],
        "low_stock": [
            {"name": p.name, "stock": p.stock, "unit": p.unit}
            for p in low_stock_products(session, store_id)
        ],
    }