"""Seed demo data for first-time onboarding.

Run once on startup only when:
  - auth is disabled (dev/demo mode), AND
  - the bootstrap user has no store yet.

When auth is enabled (CLERK_ISSUER set), seeding per-user is left to an
explicit onboarding endpoint - we never auto-create stores for real users.
"""

from __future__ import annotations

from datetime import timedelta

from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.models import Product, Store, Transaction, User
from app.models import _utcnow


DEMO_PRODUCTS = [
    # name, category, unit, price, cost, stock, threshold
    ("Nasi Goreng Ayam", "Makanan", "porsi", 18000, 9000, 40, 10),
    ("Mie Goreng Spesial", "Makanan", "porsi", 20000, 10000, 35, 10),
    ("Es Teh Manis", "Minuman", "gelas", 5000, 1500, 60, 15),
    ("Es Jeruk", "Minuman", "gelas", 7000, 2500, 45, 15),
    ("Telur Ayam", "Bahan Baku", "kg", 30000, 27000, 3, 5),
    ("Beras Premium", "Bahan Baku", "kg", 14000, 12000, 8, 10),
    ("Mie Instan", "Sembako", "bungkus", 3500, 2800, 50, 20),
    ("Kerupuk", "Pelengkap", "bungkus", 2000, 1200, 4, 10),
]

DEMO_TX = [
    ("income", "penjualan", "Nasi Goreng Ayam", 15, 18000, 1),
    ("income", "penjualan", "Es Teh Manis", 20, 5000, 1),
    ("expense", "pembelian stok", "Telur Ayam", 2, 55000, 2),
    ("income", "penjualan", "Mie Goreng Spesial", 10, 20000, 3),
    ("income", "penjualan", "Es Jeruk", 12, 7000, 3),
    ("expense", "operasional", "", 0, 25000, 4),
    ("income", "penjualan", "Nasi Goreng Ayam", 18, 18000, 5),
]


def seed_if_empty() -> None:
    """Seed the demo store for the bootstrap user (demo mode only)."""
    if settings.auth_enabled:
        # Never auto-seed real users - they onboard through the API.
        return

    with Session(engine) as session:
        bootstrap = session.exec(
            select(User).where(User.clerk_user_id == "bootstrap")
        ).first()
        if bootstrap is None:
            return

        existing_store = session.exec(
            select(Store).where(Store.owner_id == bootstrap.id)
        ).first()
        if existing_store is not None:
            return

        store = Store(
            owner_id=bootstrap.id,
            name="Warung Bu Sari",
            owner_name="Bu Sari",
            category="Warung Makan",
            currency="IDR",
            default_language="id",
            notes=(
                "Buka 08.00-21.00. Menu andalan nasi goreng dan mie goreng. "
                "Selalu tawarkan es teh manis untuk setiap pembelian makanan. "
                "Tidak melayani pengantaran di atas radius 5 km."
            ),
        )
        session.add(store)
        session.commit()
        session.refresh(store)

        products: list[Product] = []
        for name, cat, unit, price, cost, stock, thr in DEMO_PRODUCTS:
            p = Product(
                store_id=store.id,
                name=name, category=cat, unit=unit, price=price, cost=cost,
                stock=stock, low_stock_threshold=thr,
                description=f"{name} khas {store.name}.",
            )
            products.append(p)
            session.add(p)
        session.commit()
        for p in products:
            session.refresh(p)

        by_name = {p.name: p for p in products}

        for kind, category, pname, qty, total, days_ago in DEMO_TX:
            product = by_name.get(pname)
            session.add(
                Transaction(
                    store_id=store.id,
                    kind=kind,
                    category=category,
                    description=(f"{category.title()} {pname}").strip(),
                    amount=float(total * (qty if qty else 1)) if kind == "income" and qty else float(total),
                    quantity=float(qty),
                    unit=product.unit if product else "",
                    product_id=product.id if product else None,
                    product_name=pname,
                    source="manual",
                    created_at=_utcnow() - timedelta(days=days_ago),
                )
            )
        session.commit()