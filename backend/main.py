"""
Ponto de entrada da aplicação FastAPI — App Rotina Bebê 🍼
"""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import AsyncSessionLocal, create_tables
from backend.models import BathRecord, DiaperChange, FeedingRecord, SleepRecord
from backend.routers import bath, diaper, feeding, sleep
from backend.schemas import DaySummary, ReportDay


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Cria tabelas na inicialização."""
    await create_tables()
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="App Rotina Bebê 🍼",
    description="Registre amamentação, trocas, sono e banho do bebê de forma simples.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(feeding.router)
app.include_router(diaper.router)
app.include_router(sleep.router)
app.include_router(bath.router)


# ── Summary endpoint ──────────────────────────────────────────────────────────

@app.get("/api/summary", response_model=DaySummary, tags=["Resumo"])
async def get_day_summary(
    target_date: date = Query(default_factory=date.today, alias="date"),
) -> DaySummary:
    """Retorna resumo completo do dia com totais calculados."""
    async with AsyncSessionLocal() as db:
        feedings_result = await db.execute(
            select(FeedingRecord).where(FeedingRecord.date == target_date)
        )
        feedings = list(feedings_result.scalars().all())

        diapers_result = await db.execute(
            select(DiaperChange).where(DiaperChange.date == target_date)
        )
        diapers = list(diapers_result.scalars().all())

        sleeps_result = await db.execute(
            select(SleepRecord).where(SleepRecord.date == target_date)
        )
        sleeps = list(sleeps_result.scalars().all())

        baths_result = await db.execute(
            select(BathRecord).where(BathRecord.date == target_date)
        )
        baths = list(baths_result.scalars().all())

    total_ml_offered = sum(f.ml_offered or 0 for f in feedings if f.feeding_type == "bottle")
    total_ml_consumed = sum(f.ml_consumed or 0 for f in feedings if f.feeding_type == "bottle")
    
    total_breast_feedings = 0
    for f in feedings:
        if f.feeding_type in ("Breast", "breast"):
            if f.breast_side in ("left", "right"):
                total_breast_feedings += 1
            elif f.breast_side == "both":
                total_breast_feedings += 2

    total_sleep_min = sum(s.duration_min or 0 for s in sleeps)

    return DaySummary(
        date=target_date,
        feedings=feedings,
        diapers=diapers,
        sleeps=sleeps,
        baths=baths,
        total_ml_offered=total_ml_offered,
        total_ml_consumed=total_ml_consumed,
        total_diaper_changes=len(diapers),
        total_sleep_min=total_sleep_min,
        total_breast_feedings=total_breast_feedings,
    )


@app.get("/api/reports/history", response_model=list[ReportDay], tags=["Relatórios"])
async def get_reports_history() -> list[ReportDay]:
    """Retorna um histórico diário consolidado para relatórios."""
    async with AsyncSessionLocal() as db:
        feedings = list((await db.execute(select(FeedingRecord))).scalars().all())
        diapers = list((await db.execute(select(DiaperChange))).scalars().all())
        sleeps = list((await db.execute(select(SleepRecord))).scalars().all())
        baths = list((await db.execute(select(BathRecord))).scalars().all())

    reports_map: dict[date, ReportDay] = {}

    def get_day(d: date) -> ReportDay:
        if d not in reports_map:
            reports_map[d] = ReportDay(date=d)
        return reports_map[d]

    for f in feedings:
        day = get_day(f.date)
        if f.feeding_type == "bottle":
            day.total_ml_offered += f.ml_offered or 0
            day.total_ml_consumed += f.ml_consumed or 0
        elif f.feeding_type in ("Breast", "breast"):
            if f.breast_side in ("left", "right"):
                day.total_breast_feedings += 1
            elif f.breast_side == "both":
                day.total_breast_feedings += 2

    for d in diapers:
        get_day(d.date).total_diaper_changes += 1

    for s in sleeps:
        get_day(s.date).total_sleep_min += s.duration_min or 0

    for b in baths:
        get_day(b.date).total_baths += 1

    return sorted(reports_map.values(), key=lambda x: x.date, reverse=True)


# ── Static files (frontend) ───────────────────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))
