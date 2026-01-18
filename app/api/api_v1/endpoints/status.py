from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_status():
    return {"status": "online", "version": "1.0.0", "module": "core"}
