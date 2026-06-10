"""
Configuração do banco de dados async com SQLAlchemy 2.0 + SQLite (aiosqlite).
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

import os

# Em produção (Docker), a env var aponta para o volume persistente.
# Em desenvolvimento local, usa o arquivo na raiz do projeto.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./baby_routine.db",
)

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency para injetar sessão do banco nas rotas."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Cria todas as tabelas no banco de dados."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
