import os
import requests

class TelegramService:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        return response.json()

    def send_opportunity(self, job_offer):
        text = (
            f"🚀 *Nueva Oportunidad en Upwork*\n\n"
            f"📌 *Título:* {job_offer.title}\n"
            f"💰 *Presupuesto:* {job_offer.budget}\n\n"
            f"📝 *Descripción:* {job_offer.description[:300]}...\n\n"
            f"¿Quieres generar una propuesta? Responde con 'SI' o edita este mensaje."
        )
        return self.send_message(text)
