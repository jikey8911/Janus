from typing import Union
import logging
from domain.entities import ClientMessage
from domain.ports import NotificationPort

class RelayClientMessageUseCase:
    """
    Caso de Uso: Reenviar mensajes de clientes a los canales de notificación (Telegram).
    HU 4.2
    """
    def __init__(self, notification_port: NotificationPort):
        self.notification_port = notification_port

    def execute(self, message: Union[ClientMessage, str]):
        logging.info(f"Relaying message: {message}")
        try:
            success = self.notification_port.notify_message(message)
            if success:
                logging.info("Message relayed successfully.")
            else:
                logging.warning("Failed to relay message.")
        except Exception as e:
            logging.error(f"Error relaying message: {e}")
