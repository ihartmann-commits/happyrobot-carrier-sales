from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, field_validator
from typing import Optional, Union
from datetime import datetime
import uuid
import json

from database import CallRecord, get_db
from auth import verify_api_key

router = APIRouter(prefix="/calls", tags=["calls"])


class CallCreate(BaseModel):
    mc_number: Optional[str] = None
    carrier_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    load_id: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    loadboard_rate: Optional[Union[float, str]] = None
    agreed_rate: Optional[Union[float, str]] = None
    negotiation_rounds: Optional[Union[int, str]] = 0
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    fmcsa_verified: Optional[Union[bool, str]] = False
    transcript_summary: Optional[str] = None
    raw_data: Optional[dict] = None

    @field_validator("loadboard_rate", "agreed_rate", mode="before")
    @classmethod
    def parse_float(cls, v):
        if v in (None, "", "null", "None"):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @field_validator("negotiation_rounds", mode="before")
    @classmethod
    def parse_int(cls, v):
        if v in (None, "", "null", "None"):
            return 0
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            return 0

    @field_validator("fmcsa_verified", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)


@router.post("/")
async def create_call(
    call: CallCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    record = CallRecord(
        id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        mc_number=call.mc_number,
        carrier_name=call.carrier_name,
        load_id=call.load_id,
        origin=call.origin,
        destination=call.destination,
        equipment_type=call.equipment_type,
        contact_name=call.contact_name,
        contact_phone=call.contact_phone,
        contact_email=call.contact_email,
        loadboard_rate=call.loadboard_rate,
        agreed_rate=call.agreed_rate,
        negotiation_rounds=call.negotiation_rounds or 0,
        outcome=call.outcome,
        sentiment=call.sentiment,
        fmcsa_verified=1 if call.fmcsa_verified else 0,
        transcript_summary=call.transcript_summary,
        raw_data=json.dumps(call.raw_data) if call.raw_data else None,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {"id": record.id, "created_at": record.created_at}


@router.get("/")
async def list_calls(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    result = await db.execute(select(CallRecord).order_by(CallRecord.created_at.desc()))
    records = result.scalars().all()
    return {"calls": [_serialize(r) for r in records], "count": len(records)}


@router.get("/metrics/summary")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    result = await db.execute(select(CallRecord))
    records = result.scalars().all()

    total = len(records)
    if total == 0:
        return {"total_calls": 0}

    outcomes = {}
    sentiments = {}
    total_loadboard = 0.0
    total_agreed = 0.0
    booked_count = 0
    verified_count = 0
    total_rounds = 0

    for r in records:
        outcomes[r.outcome] = outcomes.get(r.outcome, 0) + 1
        sentiments[r.sentiment] = sentiments.get(r.sentiment, 0) + 1
        if r.loadboard_rate:
            total_loadboard += r.loadboard_rate
        if r.agreed_rate:
            total_agreed += r.agreed_rate
            booked_count += 1
        if r.fmcsa_verified:
            verified_count += 1
        total_rounds += r.negotiation_rounds or 0

    savings = total_loadboard - total_agreed if booked_count else 0

    return {
        "total_calls": total,
        "outcomes": outcomes,
        "sentiments": sentiments,
        "booking_rate": round(booked_count / total * 100, 1),
        "fmcsa_verified_rate": round(verified_count / total * 100, 1),
        "avg_negotiation_rounds": round(total_rounds / total, 1),
        "avg_loadboard_rate": round(total_loadboard / total, 2) if total else 0,
        "avg_agreed_rate": round(total_agreed / booked_count, 2) if booked_count else 0,
        "total_savings_vs_loadboard": round(savings, 2),
    }


@router.get("/{call_id}")
async def get_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    result = await db.execute(select(CallRecord).where(CallRecord.id == call_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Call not found")
    return _serialize(record)


def _serialize(r: CallRecord) -> dict:
    return {
        "id": r.id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "mc_number": r.mc_number,
        "carrier_name": r.carrier_name,
        "contact_name": r.contact_name,
        "contact_phone": r.contact_phone,
        "contact_email": r.contact_email,
        "load_id": r.load_id,
        "origin": r.origin,
        "destination": r.destination,
        "equipment_type": r.equipment_type,
        "loadboard_rate": r.loadboard_rate,
        "agreed_rate": r.agreed_rate,
        "negotiation_rounds": r.negotiation_rounds,
        "outcome": r.outcome,
        "sentiment": r.sentiment,
        "fmcsa_verified": bool(r.fmcsa_verified),
        "transcript_summary": r.transcript_summary,
    }
