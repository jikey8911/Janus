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

    def send_opportunity_with_proposal(self, job_offer, ai_analysis):
        text = (
            f"🚀 *Nueva Oportunidad Detectada*\n\n"
            f"📌 *Título:* {job_offer.title}\n"
            f"💰 *Presupuesto:* {job_offer.budget}\n"
            f"📊 *Puntuación IA:* {ai_analysis.get('score')}/100\n\n"
            f"🧐 *Análisis:* {ai_analysis.get('analysis')}\n\n"
            f"📝 *Propuesta Sugerida:*\n{ai_analysis.get('proposal')}\n\n"
            f"--- \n"
            f"✅ Responde 'ENVIAR' para mandarla tal cual.\n"
            f"✏️ O responde con el texto editado para enviarla."
        )
        return self.send_message(text)

    def notify_client_message(self, client_name, message, suggested_reply):
        text = (
            f"📩 *Nuevo Mensaje del Cliente: {client_name}*\n\n"
            f"💬 *Mensaje:* {message}\n\n"
            f"🤖 *Respuesta Sugerida:*\n{suggested_reply}\n\n"
            f"--- \n"
            f"✅ Responde 'RESPONDER' para enviar la sugerencia.\n"
            f"✏️ O envía tu propia respuesta."
        )
        return self.send_message(text)
