"""Core business operations shared by both the REST API and the AI tools.

Keeping the logic here (rather than inside route handlers or tool wrappers)
means the AI agent and the dashboard mutate data through the exact same paths.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import Product, Transaction


def find_product(session: Session, name: str) -> Product | None:
    """Case-insensitive best-effort product lookup by name."""
    if not name:
        return None
    name_l = name.strip().lower()
    products = session.exec(select(Product)).all()
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
    product_name: str,
    quantity: float,
    amount: float | None = None,
    unit: str = "",
    description: str = "",
    source: str = "manual",
) -> Transaction:
    """Record an income transaction and decrement stock if the product exists."""
    product = find_product(session, product_name)
    resolved_unit = unit
    if product:
        if amount is None:
            amount = product.price * quantity
        product.stock = max(0.0, product.stock - quantity)
        product.updated_at = datetime.now(timezone.utc)
        resolved_unit = unit or product.unit
        session.add(product)

    tx = Transaction(
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
    product = find_product(session, product_name) if product_name else None
    resolved_unit = unit
    if product and add_to_stock and quantity:
        product.stock += quantity
        product.updated_at = datetime.now(timezone.utc)
        resolved_unit = unit or product.unit
        session.add(product)

    tx = Transaction(
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


def set_stock(session: Session, product_name: str, stock: float) -> Product | None:
    product = find_product(session, product_name)
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
    name: str,
    price: float = 0.0,
    stock: float = 0.0,
    unit: str = "pcs",
    category: str = "",
    cost: float = 0.0,
    description: str = "",
) -> Product:
    product = find_product(session, name)
    if product:
        product.price = price or product.price
        product.stock = stock if stock else product.stock
        product.unit = unit or product.unit
        product.category = category or product.category
        product.cost = cost or product.cost
        product.description = description or product.description
        product.updated_at = datetime.now(timezone.utc)
    else:
        product = Product(
            name=name,
            price=price,
            stock=stock,
            unit=unit,
            category=category,
            cost=cost,
            description=description,
        )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def low_stock_products(session: Session) -> list[Product]:
    return [
        p
        for p in session.exec(select(Product)).all()
        if p.stock <= p.low_stock_threshold
    ]


def sales_summary(session: Session, days: int = 7) -> dict:
    """Aggregate income/expense over the trailing `days` window."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    txs = session.exec(
        select(Transaction).where(Transaction.created_at >= since)
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
            for p in low_stock_products(session)
        ],
    }
