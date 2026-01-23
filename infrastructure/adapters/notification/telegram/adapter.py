import os
import logging
import requests
from typing import Union, Optional, List, Dict
from domain.ports import NotificationPort
from domain.entities import JobOffer, ClientMessage

class TelegramAdapter(NotificationPort):
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def _send_text(self, text: str, parse_mode: str = "Markdown", reply_markup: Optional[Dict] = None) -> bool:
        """Envía un mensaje de texto a Telegram."""
        if not self.bot_token or not self.chat_id:
            logging.warning("Telegram credentials not configured")
            return False
        
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logging.info("Telegram message sent successfully")
            return True
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            return False

    def send_proposal_for_validation(
        self, 
        job_title: str, 
        proposal_content: str, 
        proposal_id: int,
        job_id: str,
        analysis_score: Optional[int] = None,
        bid_amount: Optional[float] = None,
        currency: Optional[str] = "USD"
    ) -> bool:
        """
        Envía una propuesta a Telegram con botones de aprobación/rechazo.
        """
        # Construir mensaje
        score_emoji = "🟢" if analysis_score and analysis_score >= 80 else "🟡" if analysis_score and analysis_score >= 60 else "🔴"
        score_text = f"{score_emoji} Score: {analysis_score}/100\n" if analysis_score else ""
        bid_text = f"💰 **Monto Sugerido:** {bid_amount} {currency}\n" if bid_amount else ""
        
        message = f"""📝 **PROPUESTA GENERADA**
 
 **Trabajo:** {job_title}
 **ID:** `{job_id}`
 {score_text}{bid_text}
 ---

{proposal_content}

---
👇 **Selecciona una acción:**
"""
        
        # Crear inline keyboard
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Aprobar y Enviar", "callback_data": f"approve_{proposal_id}"},
                    {"text": "❌ Rechazar", "callback_data": f"reject_{proposal_id}"}
                ],
                [
                    {"text": "✏️ Editar", "callback_data": f"edit_{proposal_id}"},
                    {"text": "📊 Ver Análisis", "callback_data": f"analysis_{job_id}"}
                ]
            ]
        }
        
        return self._send_text(message, reply_markup=inline_keyboard)

    def notify_opportunity(self, job: JobOffer, analysis: dict) -> bool:
        """Notifica una nueva oportunidad con su análisis."""
        score = analysis.get('score', 0)
        viability = analysis.get('viability_analysis', 'N/A')
        
        # Emoji según score
        if score >= 80:
            emoji = "🟢"
        elif score >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        message = f"""{emoji} **NUEVA OPORTUNIDAD**

**Título:** {job.title}
**ID:** `{job.external_id}`
**Presupuesto:** {job.budget}
**Score:** {score}/100

**Análisis:**
{viability}

---
Usa `/generate {job.external_id}` para crear propuesta
"""
        
        return self._send_text(message)

    def notify_message(self, message: Union[ClientMessage, str]) -> bool:
        """Envía un mensaje genérico."""
        text = message.content if isinstance(message, ClientMessage) else str(message)
        return self._send_text(text)

