import sys
import os
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

import logging
import requests
from typing import Union
from domain.entities import JobOffer, ClientMessage
from domain.ports import NotificationPort

# ADAPTER DEFINED INLINE TO AVOID IMPORT NULL BYTE ISSUE
class TelegramAdapter(NotificationPort):
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _send_text(self, text: str) -> bool:
        if not self.bot_token:
            logging.warning("Telegram credentials not found. Notification skipped.")
            return False

        try:
            # FORCE HARDCODED CHAT ID IF ENV FAILS
            target_chat_id = self.chat_id or "6092013092"
            
            payload = {
                "chat_id": target_chat_id,
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
            f"**Titulo:** {job.title}\n"
            f"**Presupuesto:** {job.budget}\n"
            f"**Categoria:** #{job.category or 'General'}\n\n"
            f"**Resumen:** {job.description[:250]}...\n\n"
            f"**Analisis IA:** {reasoning}\n\n"
            f"LINK [Ver en Upwork](https://www.upwork.com/jobs/{job.upwork_id})\n"
            f"ID `{job.upwork_id}`\n"
            f"ACCIONES:\n"
            f"`/generate {job.upwork_id}`"
        )
        return self._send_text(message)

    def notify_message(self, message: Union[ClientMessage, str]) -> bool:
        if isinstance(message, str):
            text = f"INFO **Sistema Janus:**\n{message}"
        else:
            text = (
                f"MSG **Nuevo Mensaje de Cliente**\n\n"
                f"**Cliente:** {message.client_name}\n"
                f"**Contenido:** {message.message_content}\n"
                f"**Contexto:** {message.job_context}"
            )
        return self._send_text(text)

logging.basicConfig(level=logging.INFO)

def run_demo():
    print("🚀 Iniciando Demo de Flujo Completo Janus V2.1 (Monolito)")
    
    job = JobOffer(
        upwork_id="TEST_JOB_999",
        title="Python Developer Needed (Demo)",
        description="Looking for an expert to verify Janus Flow. Pays well.",
        budget="$1000",
        category="Software Development",
        status="pending"
    )
    
    analysis = {
        "score": 95,
        "reasoning": "This job matches perfectly with Janus capabilities."
    }
    
    print("3. Enviando notificación a Telegram (Inline Adapter)...")
    adapter = TelegramAdapter()
    
    success = adapter.notify_opportunity(job, analysis)
    
    if success:
        print("\n✅ Notificación enviada con éxito.")
        print("👉 POR FAVOR, REVISA TU TELEGRAM.")
    else:
        print("❌ Falló el envío de notificación.")

if __name__ == "__main__":
    run_demo()
