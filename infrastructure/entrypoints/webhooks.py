from fastapi import FastAPI, Request, HTTPException
import logging
from domain.entities import ClientMessage
from application.relay_use_case import RelayClientMessageUseCase
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración Manual de Dependencias (Idealmente usar Dependency Injection)
telegram_adapter = TelegramAdapter()
relay_use_case = RelayClientMessageUseCase(notification_port=telegram_adapter)

@app.post("/webhooks/freelancer")
async def freelancer_webhook(request: Request):
    """
    Endpoint para recibir eventos (Push) de Freelancer.com o simulador.
    """
    try:
        payload = await request.json()
        logger.info(f"Webhook recibido de Freelancer: {payload}")
        
        event_type = payload.get("type", "unknown")
        
        if event_type == "message":
            # Mapeo de Payload a Entidad de Dominio
            message = ClientMessage(
                client_name=payload.get("data", {}).get("from_user", "Unknown Client"),
                message_content=payload.get("data", {}).get("text", ""),
                job_context=payload.get("data", {}).get("context", "Freelancer Project"),
                id=None # ID interno nulo por ahora
            )
            
            logger.info("Procesando mensaje entrante...")
            relay_use_case.execute(message)
            
            return {"status": "processed", "type": "message"}
        
        elif event_type == "job_awarded":
            logger.info("Oferta ganada! Iniciando protocolo.")
            return {"status": "processed", "type": "job_awarded"}

        return {"status": "ignored", "reason": "unknown_event"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.get("/health")
def health_check():
    return {"status": "ok"}
