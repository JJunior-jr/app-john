"""
Ponto de entrada da aplicação FastAPI — App Rotina Bebê 🍼
"""
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, or_
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
            select(SleepRecord).where(
                or_(
                    SleepRecord.date == target_date,
                    SleepRecord.date == target_date - timedelta(days=1)
                )
            ).order_by(SleepRecord.start_time)
        )
        sleeps = list(sleeps_result.scalars().all())

        last_sleep_result = await db.execute(
            select(SleepRecord).order_by(SleepRecord.start_time.desc()).limit(1)
        )
        last_sleep = last_sleep_result.scalars().first()

        last_feeding_result = await db.execute(
            select(FeedingRecord).order_by(FeedingRecord.recorded_at.desc()).limit(1)
        )
        last_feeding = last_feeding_result.scalars().first()

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

    # Lógica de fatiamento do sono
    target_start = datetime.combine(target_date, datetime.min.time(), tzinfo=ZoneInfo("America/Sao_Paulo"))
    target_end = datetime.combine(target_date, datetime.max.time(), tzinfo=ZoneInfo("America/Sao_Paulo"))
    now = datetime.now(ZoneInfo('America/Sao_Paulo'))
    
    valid_sleeps_for_response = []
    total_sleep_seconds = 0
    
    for s in sleeps:
        s_start = s.start_time
        if s_start.tzinfo is None:
            s_start = s_start.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            
        s_end = s.end_time
        if s_end is None:
            s_end = now
        elif s_end.tzinfo is None:
            s_end = s_end.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            
        overlap_start = max(s_start, target_start)
        overlap_end = min(s_end, target_end)
        
        if overlap_start < overlap_end:
            total_sleep_seconds += (overlap_end - overlap_start).total_seconds()
            valid_sleeps_for_response.append(s)

    total_sleep_min = round(total_sleep_seconds / 60, 1)

    # Tempo Total Acordado
    if target_date == now.date():
        total_time_in_day = max(0, (now - target_start).total_seconds())
    elif target_date < now.date():
        total_time_in_day = 24 * 3600
    else:
        total_time_in_day = 0
        
    total_awake_min = max(0, round((total_time_in_day - total_sleep_seconds) / 60, 1))

    # Tempo Acordado Atual
    current_awake_time_min = None
    if target_date == now.date() and last_sleep:
        if last_sleep.end_time is None:
            current_awake_time_min = 0.0
        else:
            ls_end = last_sleep.end_time
            if ls_end.tzinfo is None:
                ls_end = ls_end.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            if ls_end <= now:
                current_awake_time_min = round((now - ls_end).total_seconds() / 60, 1)

    # Tempo Sem Comer Atual
    current_fasting_time_min = None
    if target_date == now.date() and last_feeding:
        lf_time = last_feeding.recorded_at
        if lf_time.tzinfo is None:
            lf_time = lf_time.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
        if lf_time <= now:
            current_fasting_time_min = round((now - lf_time).total_seconds() / 60, 1)

    return DaySummary(
        date=target_date,
        feedings=feedings,
        diapers=diapers,
        sleeps=valid_sleeps_for_response,
        baths=baths,
        total_ml_offered=total_ml_offered,
        total_ml_consumed=total_ml_consumed,
        total_diaper_changes=len(diapers),
        total_sleep_min=total_sleep_min,
        total_awake_min=total_awake_min,
        current_awake_time_min=current_awake_time_min,
        current_fasting_time_min=current_fasting_time_min,
        total_breast_feedings=total_breast_feedings,
    )


@app.get("/api/reports/history", response_model=list[ReportDay], tags=["Relatórios"])
async def get_reports_history() -> list[ReportDay]:
    """Retorna um histórico diário consolidado para relatórios."""
    async with AsyncSessionLocal() as db:
        feedings = list((await db.execute(select(FeedingRecord).order_by(FeedingRecord.recorded_at))).scalars().all())
        diapers = list((await db.execute(select(DiaperChange))).scalars().all())
        sleeps = list((await db.execute(select(SleepRecord).order_by(SleepRecord.start_time))).scalars().all())
        baths = list((await db.execute(select(BathRecord))).scalars().all())

    reports_map: dict[date, ReportDay] = {}

    def get_day(d: date) -> ReportDay:
        if d not in reports_map:
            reports_map[d] = ReportDay(date=d)
        return reports_map[d]

    now = datetime.now(ZoneInfo('America/Sao_Paulo'))
    last_feeding_time = None

    for f in feedings:
        day = get_day(f.date)
        day.feedings_count += 1
        if f.feeding_type == "bottle":
            day.total_ml_offered += f.ml_offered or 0
            day.total_ml_consumed += f.ml_consumed or 0
        elif f.feeding_type in ("Breast", "breast"):
            if f.breast_side in ("left", "right"):
                day.total_breast_feedings += 1
            elif f.breast_side == "both":
                day.total_breast_feedings += 2

        current_time = f.recorded_at
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))

        if last_feeding_time:
            fasting_min = (current_time - last_feeding_time).total_seconds() / 60
            if fasting_min > day.max_fasting_min:
                day.max_fasting_min = fasting_min
        last_feeding_time = current_time

    for d in diapers:
        get_day(d.date).total_diaper_changes += 1

    for s in sleeps:
        s_start = s.start_time
        if s_start.tzinfo is None:
            s_start = s_start.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            
        s_end = s.end_time
        if s_end is None:
            s_end = now
        elif s_end.tzinfo is None:
            s_end = s_end.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            
        current = s_start
        while current < s_end:
            current_date = current.date()
            next_day = datetime.combine(current_date + timedelta(days=1), datetime.min.time(), tzinfo=ZoneInfo("America/Sao_Paulo"))
            end_of_chunk = min(s_end, next_day)
            
            chunk_min = (end_of_chunk - current).total_seconds() / 60
            day = get_day(current_date)
            day.total_sleep_min += chunk_min
            
            if current == s_start:
                day.sleeps_count += 1
                
            current = next_day

    for b in baths:
        get_day(b.date).total_baths += 1

    for d, day_obj in reports_map.items():
        if d == now.date():
            day_start = datetime.combine(d, datetime.min.time(), tzinfo=ZoneInfo("America/Sao_Paulo"))
            total_time_in_day_min = max(0, (now - day_start).total_seconds() / 60)
        elif d < now.date():
            total_time_in_day_min = 24 * 60
        else:
            total_time_in_day_min = 0
            
        day_obj.total_awake_min = max(0, round(total_time_in_day_min - day_obj.total_sleep_min, 1))
        day_obj.total_sleep_min = round(day_obj.total_sleep_min, 1)
        day_obj.max_fasting_min = round(day_obj.max_fasting_min, 1)
        if day_obj.sleeps_count > 0:
            day_obj.avg_sleep_min = round(day_obj.total_sleep_min / day_obj.sleeps_count, 1)

    return sorted(reports_map.values(), key=lambda x: x.date, reverse=True)


# ── Static files (frontend) ───────────────────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))
