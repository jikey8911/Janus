from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_status():
    return {"status": "online", "version": "2.0.0", "module": "core"}
