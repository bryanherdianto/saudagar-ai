"""Database engine and session management using SQLModel + SQLite."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# `check_same_thread` is only relevant for SQLite; FastAPI accesses the
# connection from worker threads.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Create tables. Import models so they register on SQLModel.metadata."""
    from app import models  # noqa: F401  (side-effect: register tables)

    SQLModel.metadata.create_all(engine)
    _migrate_legacy_schema()


def _migrate_legacy_schema() -> None:
    """Backfill the multi-tenant columns (`owner_id`, `store_id`) on existing
    rows from the old single-tenant schema.

    Strategy: ensure the columns exist (idempotent), create a bootstrap user
    if any orphan rows need an owner, then stamp orphan `store`, `product`,
    and `transaction` rows with the bootstrap user/store ids.
    """
    inspector = inspect(engine)
    if "store" not in inspector.get_table_names():
        return

    # Ensure new columns exist — ALTER TABLE ADD COLUMN is idempotent via try/except.
    def _add_column(table: str, column: str, ddl: str) -> None:
        cols = {c["name"] for c in inspector.get_columns(table)}
        if column not in cols:
            with engine.begin() as conn:
                # Quote the table name — `transaction` is a reserved SQLite keyword.
                conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {ddl}'))

    _add_column("store", "owner_id", "owner_id INTEGER REFERENCES user(id)")
    _add_column("product", "store_id", "store_id INTEGER REFERENCES store(id)")
    _add_column("transaction", "store_id", "store_id INTEGER REFERENCES store(id)")

    # Create the bootstrap user (clerk_user_id="bootstrap") if there are
    # orphaned stores needing an owner.
    from sqlmodel import select

    from app.models import User

    with Session(engine) as session:
        orphan_count = session.connection().execute(
            text("SELECT COUNT(*) FROM store WHERE owner_id IS NULL")
        ).scalar_one()
        if orphan_count:
            bootstrap = session.exec(
                select(User).where(User.clerk_user_id == "bootstrap")
            ).first()
            if bootstrap is None:
                bootstrap = User(clerk_user_id="bootstrap", name="Bootstrap Owner")
                session.add(bootstrap)
                session.commit()
                session.refresh(bootstrap)
            uid = bootstrap.id
            # Re-acquire the connection: the commit above ended the previous
            # transaction and released the earlier connection object.
            conn = session.connection()
            conn.execute(
                text("UPDATE store SET owner_id = :uid WHERE owner_id IS NULL"),
                {"uid": uid},
            )
            conn.execute(
                text(
                    "UPDATE product SET store_id = "
                    "(SELECT MIN(id) FROM store WHERE owner_id = :uid) "
                    "WHERE store_id IS NULL"
                ),
                {"uid": uid},
            )
            conn.execute(
                text(
                    'UPDATE "transaction" SET store_id = '
                    "(SELECT MIN(id) FROM store WHERE owner_id = :uid) "
                    "WHERE store_id IS NULL"
                ),
                {"uid": uid},
            )
            session.commit()


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session (unscoped)."""
    with Session(engine) as session:
        yield session