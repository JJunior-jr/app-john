"""Router de amamentação."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import FeedingRecord
from backend.schemas import FeedingCreate, FeedingResponse

from backend.schemas import FeedingCreate, FeedingResponse, FeedingUpdate # <--- Adicione FeedingUpdate

router = APIRouter(prefix="/api/feeding", tags=["Amamentação"])


@router.post("", response_model=FeedingResponse, status_code=201)
async def create_feeding(
    payload: FeedingCreate,
    db: AsyncSession = Depends(get_db),
) -> FeedingRecord:
    """Registra uma nova alimentação. Horário é automático (agora)."""
    now = datetime.now(ZoneInfo('America/Sao_Paulo'))
    record = FeedingRecord(
        recorded_at=now,
        date=now.date(),
        feeding_type=payload.feeding_type,
        ml_offered=payload.ml_offered,
        ml_consumed=payload.ml_consumed,
        breast_side=payload.breast_side,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.get("", response_model=list[FeedingResponse])
async def list_feedings(
    date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
) -> list[FeedingRecord]:
    """Lista todos os registros de alimentação de um dia."""
    result = await db.execute(
        select(FeedingRecord)
        .where(FeedingRecord.date == date)
        .order_by(FeedingRecord.recorded_at)
    )
    return list(result.scalars().all())


@router.delete("/{record_id}", status_code=204)
async def delete_feeding(
    record_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove um registro de alimentação."""
    record = await db.get(FeedingRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    await db.delete(record)

@router.put("/{record_id}", response_model=FeedingResponse)
async def update_feeding(
    record_id: int,
    payload: FeedingUpdate,
    db: AsyncSession = Depends(get_db),
) -> FeedingRecord:
    """Atualiza as informações e/ou horário de um registro de alimentação."""
    record = await db.get(FeedingRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    if payload.recorded_at is not None:
        record.recorded_at = payload.recorded_at
        record.date = payload.recorded_at.date()
        
    if payload.ml_offered is not None:
        record.ml_offered = payload.ml_offered
        
    if payload.ml_consumed is not None:
        record.ml_consumed = payload.ml_consumed
        
    if payload.breast_side is not None:
        record.breast_side = payload.breast_side
        
    await db.flush()
    await db.refresh(record)
    return record