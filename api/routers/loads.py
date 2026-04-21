from fastapi import APIRouter, Depends, Query
from typing import Optional
import json
import os

from auth import verify_api_key

STATE_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}


def normalize(query: str) -> list[str]:
    q = query.lower().strip()
    terms = [q]
    if q in STATE_ABBR:
        terms.append(STATE_ABBR[q].lower())
    return terms

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
        terms = normalize(origin)
        loads = [l for l in loads if any(t in l["origin"].lower() for t in terms)]
    if destination:
        terms = normalize(destination)
        loads = [l for l in loads if any(t in l["destination"].lower() for t in terms)]
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
