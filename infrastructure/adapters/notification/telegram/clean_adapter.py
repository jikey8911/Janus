import os
import logging
import requests
from typing import Union
from domain.ports import NotificationPort
from domain.entities import JobOffer, ClientMessage

class TelegramAdapter(NotificationPort):
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
        score = analysis.get("score", 0)
        reasoning = analysis.get("reasoning", "No analysis")
        icon = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        
        message = (
            f"{icon} **Nueva Oportunidad Detectada** (Score: {score}/100)\n\n"
            f"**Título:** {job.title}\n"
            f"**Presupuesto:** {job.budget}\n"
            f"**Categoría:** #{job.category or 'General'}\n\n"
            f"**Resumen:** {job.description[:250]}...\n\n"
            f"**Análisis IA:** {reasoning}\n\n"
            f"🔗 [Ver en Upwork](https://www.upwork.com/jobs/{job.upwork_id})\n"
            f"🆔 `{job.upwork_id}`\n"
            f"👇 **Acciones:**\n"
            f"`/generate {job.upwork_id}`"
        )
        return self._send_text(message)

    def notify_message(self, message: Union[ClientMessage, str]) -> bool:
        if isinstance(message, str):
            text = f"ℹ️ **Sistema Janus:**\n{message}"
        else:
            text = (
                f"📩 **Nuevo Mensaje de Cliente**\n\n"
                f"**Cliente:** {message.client_name}\n"
                f"**Contenido:** {message.message_content}\n"
                f"**Contexto:** {message.job_context}"
            )
        return self._send_text(text)
