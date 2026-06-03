from fastapi import APIRouter, Request

router = APIRouter()

_STORAGE: dict[str, dict] = {}

@router.get("/api/state")
async def get_state():
    return _STORAGE.get("state", {})

@router.post("/api/state")
async def save_state(request: Request):
    payload = await request.json()
    _STORAGE["state"] = payload
    return {"ok": True}
