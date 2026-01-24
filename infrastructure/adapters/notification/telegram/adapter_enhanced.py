import os
import logging
import requests
from typing import Union
from domain.ports import NotificationPort
from domain.entities import JobOffer, ClientMessage

class TelegramAdapterEnhanced(NotificationPort):
    """Adaptador mejorado de Telegram con soporte para planes de implementación."""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _send_text(self, text: str) -> bool:
        if not self.bot_token or not self.chat_id:
            logging.warning("Telegram credentials not found. Notification skipped.")
            logging.info(f"[MOCK TELEGRAM] {text}")
            return False

        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.base_url, json=payload, timeout=10)
            if response.status_code == 200:
                logging.info("Telegram notification sent successfully.")
                return True
            else:
                logging.error(f"Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            return False

    def notify_opportunity(self, job: JobOffer, analysis: dict) -> bool:
        """Notifica una oportunidad con análisis."""
        score = analysis.get("score", 0)
        reasoning = analysis.get("analysis", "No analysis")
        proposal = analysis.get("proposal", "No proposal generated")
        
        icon = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        
        message = (
            f"{icon} **Nueva Oportunidad Detectada** (Score: {score}/100)\n\n"
            f"**Título:** {job.title}\n"
            f"**Presupuesto:** {job.budget}\n\n"
            f"**Análisis IA:** {reasoning}\n\n"
            f"**Propuesta Sugerida:**\n`{proposal}`\n\n"
            f"🆔 `{job.upwork_id}`\n\n"
            f"👇 **Acciones:**\n"
            f"✅ `/enviar {job.upwork_id}`\n"
            f"✏️ Responde a este mensaje para editar la propuesta."
        )
        return self._send_text(message)

    def notify_message(self, message: Union[ClientMessage, str]) -> bool:
        """Notifica un mensaje de cliente."""
        if isinstance(message, str):
            text = f"ℹ️ **Sistema Janus:**\n{message}"
        else:
            text = (
                f"📩 **Nuevo Mensaje de Cliente**\n\n"
                f"**Cliente:** {message.client_name}\n"
                f"**Contenido:** {message.message_content}\n\n"
                f"🤖 **Respuesta Sugerida:**\n`{message.suggested_reply}`\n\n"
                f"👇 **Acciones:**\n"
                f"✅ `/responder {message.client_name}`"
            )
        return self._send_text(text)

    def notify_implementation_plan(self, job: JobOffer, plan: dict) -> bool:
        """Notifica un plan de implementación para aprobación."""
        phases_text = ""
        for phase in plan.get("phases", []):
            phases_text += (
                f"\n**Fase {phase['phase']}: {phase['name']}** ({phase['duration']})\n"
            )
            for task in phase.get("tasks", []):
                phases_text += f"  • {task}\n"
        
        message = (
            f"📋 **Plan de Implementación Generado**\n\n"
            f"**Proyecto:** {job.title}\n"
            f"**Categoría:** {plan.get('category', 'General')}\n"
            f"**Duración Estimada:** {plan.get('estimated_duration', 'N/A')}\n"
            f"{phases_text}\n"
            f"**Entregables:**\n"
        )
        
        for deliverable in plan.get("deliverables", []):
            message += f"  ✓ {deliverable}\n"
        
        message += (
            f"\n🆔 `{job.upwork_id}`\n\n"
            f"👇 **Acciones:**\n"
            f"✅ `/aprobar {job.upwork_id}` - Aprobar y enviar a cliente\n"
            f"✏️ Responde para editar el plan"
        )
        
        return self._send_text(message)
