from fastapi import APIRouter, Depends
import httpx
import os

from auth import verify_api_key

router = APIRouter(prefix="/fmcsa", tags=["fmcsa"])

FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services/carriers"

# Mock carriers for demo/testing when FMCSA API is unavailable
MOCK_CARRIERS = {
    "123456": {"eligible": True, "legal_name": "Swift Transportation Co", "dot_number": "999001"},
    "654321": {"eligible": True, "legal_name": "Werner Enterprises", "dot_number": "999002"},
    "111111": {"eligible": False, "legal_name": "Revoked Carrier LLC", "dot_number": "999003"},
    "999999": {"eligible": False, "legal_name": "Inactive Carrier Inc", "dot_number": "999004"},
}


@router.get("/verify/{mc_number}")
async def verify_carrier_path(mc_number: str, _: str = Depends(verify_api_key)):
    return await _verify(mc_number)


@router.get("/verify")
async def verify_carrier(mc_number: str = "", _: str = Depends(verify_api_key)):
    return await _verify(mc_number)


async def _verify(mc_number: str):
    api_key = os.getenv("FMCSA_API_KEY")

    # Try real FMCSA API first
    url = f"{FMCSA_BASE}/docket-number/{mc_number}?webKey={api_key}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("content", [])
                if content and len(content) > 0:
                    carrier = content[0].get("carrier", {})
                    if carrier:
                        allowed_to_operate = carrier.get("allowedToOperate", "N")
                        eligible = allowed_to_operate == "Y"
                        return {
                            "eligible": eligible,
                            "reason": "Carrier is authorized to operate" if eligible else "Carrier is NOT authorized to operate",
                            "mc_number": mc_number,
                            "dot_number": str(carrier.get("dotNumber", "")),
                            "legal_name": carrier.get("legalName", "Unknown"),
                            "allowed_to_operate": allowed_to_operate,
                        }
    except httpx.RequestError:
        pass

    # Fall back to mock data for demo purposes
    mock = MOCK_CARRIERS.get(mc_number)
    if mock:
        return {
            "eligible": mock["eligible"],
            "reason": "Carrier is authorized to operate" if mock["eligible"] else "Carrier is NOT authorized to operate",
            "mc_number": mc_number,
            "dot_number": mock["dot_number"],
            "legal_name": mock["legal_name"],
            "allowed_to_operate": "Y" if mock["eligible"] else "N",
        }

    # Unknown MC number — treat as not found
    return {
        "eligible": False,
        "reason": "Carrier not found in FMCSA database",
        "mc_number": mc_number,
        "dot_number": "",
        "legal_name": "Unknown",
        "allowed_to_operate": "N",
    }
