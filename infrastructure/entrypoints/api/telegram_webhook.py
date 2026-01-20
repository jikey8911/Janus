from fastapi import APIRouter, Request
from app.core.telegram_service import TelegramService
from app.core.upwork_service import UpworkService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Lógica de procesamiento de comandos
        telegram_ws = TelegramService()
        upwork_ws = UpworkService()
        
        if text.upper() == "ENVIAR":
            # Aquí buscaríamos la última propuesta generada en la DB
            # Por ahora simulamos el envío
            telegram_ws.send_message("✅ ¡Entendido! Enviando propuesta a Upwork...")
            # upwork_ws.submit_proposal(job_id, proposal_text)
            
        elif text.upper() == "RESPONDER":
            telegram_ws.send_message("✅ Enviando respuesta sugerida al cliente...")
            
        else:
            # Si el texto no es un comando, asumimos que es una edición
            telegram_ws.send_message(f"📝 He recibido tu edición. ¿Quieres que envíe este texto como propuesta?\n\n{text}")
            
    return {"status": "ok"}
