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
        if not self.bot_token or not self.chat_id: return False
        try:
            requests.post(self.base_url, json={"chat_id": self.chat_id, "text": text}, timeout=10)
            return True
        except: return False

    def notify_opportunity(self, job: JobOffer, analysis: dict) -> bool:
        return self._send_text(f"New Job: {job.title}")

    def notify_message(self, message: Union[ClientMessage, str]) -> bool:
        return self._send_text(str(message))
