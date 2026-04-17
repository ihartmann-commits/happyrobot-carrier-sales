from fastapi import APIRouter, Depends
import httpx
import os

from auth import verify_api_key

router = APIRouter(prefix="/fmcsa", tags=["fmcsa"])

FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services/carriers"


@router.get("/verify/{mc_number}")
async def verify_carrier(mc_number: str, _: str = Depends(verify_api_key)):
    api_key = os.getenv("FMCSA_API_KEY")
    url = f"{FMCSA_BASE}/mc/{mc_number}?webKey={api_key}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return {"eligible": False, "reason": "Carrier not found in FMCSA database", "mc_number": mc_number}

            data = resp.json()
            carrier = data.get("content", {}).get("carrier", {})

            if not carrier:
                return {"eligible": False, "reason": "No carrier data returned", "mc_number": mc_number}

            allowed_to_operate = carrier.get("allowedToOperate", "N")
            carrier_operation = carrier.get("carrierOperation", {})
            legal_name = carrier.get("legalName", "Unknown")
            dot_number = carrier.get("dotNumber", "")

            eligible = allowed_to_operate == "Y"
            reason = "Carrier is authorized to operate" if eligible else "Carrier is NOT authorized to operate"

            return {
                "eligible": eligible,
                "reason": reason,
                "mc_number": mc_number,
                "dot_number": dot_number,
                "legal_name": legal_name,
                "carrier_operation": carrier_operation,
                "allowed_to_operate": allowed_to_operate,
            }

    except httpx.RequestError as e:
        return {"eligible": False, "reason": f"FMCSA API error: {str(e)}", "mc_number": mc_number}
