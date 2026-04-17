from fastapi import APIRouter, Depends, Query
from typing import Optional
import json
import os

from auth import verify_api_key

router = APIRouter(prefix="/loads", tags=["loads"])

LOADS_FILE = os.path.join(os.path.dirname(__file__), "../../data/loads.json")


def load_data():
    with open(LOADS_FILE, "r") as f:
        return json.load(f)


@router.get("/")
async def search_loads(
    origin: Optional[str] = Query(None, description="Filter by origin city/state"),
    destination: Optional[str] = Query(None, description="Filter by destination city/state"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    _: str = Depends(verify_api_key),
):
    loads = load_data()

    if origin:
        loads = [l for l in loads if origin.lower() in l["origin"].lower()]
    if destination:
        loads = [l for l in loads if destination.lower() in l["destination"].lower()]
    if equipment_type:
        loads = [l for l in loads if equipment_type.lower() in l["equipment_type"].lower()]

    return {"loads": loads, "count": len(loads)}


@router.get("/{load_id}")
async def get_load(load_id: str, _: str = Depends(verify_api_key)):
    loads = load_data()
    for load in loads:
        if load["load_id"] == load_id:
            return load
    return {"error": "Load not found"}
