from fastapi import APIRouter, Request, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Endpoint para recibir webhooks de Telegram.
    """
    try:
        payload = await request.json()
        logger.info(f"Webhook recibido de Telegram: {payload}")
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Error procesando webhook de Telegram: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")
