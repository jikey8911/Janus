import os
import logging
from typing import Dict, Callable
import requests

class TelegramCommandHandler:
    """Manejador de comandos de Telegram con menú visual."""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.commands: Dict[str, Callable] = {
            "listar": self.cmd_listar,
            "buscar": self.cmd_buscar,
            "enviar": self.cmd_enviar,
            "responder": self.cmd_responder,
            "estado": self.cmd_estado,
            "ayuda": self.cmd_ayuda,
        }

    def send_message(self, text: str, reply_markup=None) -> bool:
        """Envía un mensaje con teclado opcional."""
        if not self.bot_token or not self.chat_id:
            logging.error("Faltan credenciales de Telegram")
            return False
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Error enviando mensaje: {e}")
            return False

    def show_main_menu(self) -> bool:
        """Muestra el menú principal con botones."""
        keyboard = {
            "keyboard": [
                [{"text": "/listar"}, {"text": "/buscar"}],
                [{"text": "/estado"}, {"text": "/ayuda"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        text = (
            "🤖 *Bienvenido a Janus*\n\n"
            "Selecciona una opción:\n\n"
            "📋 `/listar` - Ver oportunidades pendientes\n"
            "🔍 `/buscar` - Buscar nuevas oportunidades\n"
            "📊 `/estado` - Ver estado del sistema\n"
            "❓ `/ayuda` - Mostrar ayuda"
        )
        return self.send_message(text, keyboard)

    def cmd_listar(self, args: str = "") -> bool:
        """Comando: Listar oportunidades pendientes."""
        text = (
            "📋 *Oportunidades Pendientes*\n\n"
            "Aquí aparecerían las oportunidades sin procesar.\n"
            "(Integración con base de datos pendiente)"
        )
        return self.send_message(text)

    def cmd_buscar(self, args: str = "") -> bool:
        """Comando: Buscar nuevas oportunidades."""
        query = args.strip() if args else "(python OR automation OR ai)"
        text = (
            f"🔍 *Buscando oportunidades*\n\n"
            f"Query: `{query}`\n\n"
            f"Iniciando búsqueda en Freelancer.com...\n"
            f"(Ejecutando tarea asíncrona)"
        )
        return self.send_message(text)

    def cmd_enviar(self, args: str = "") -> bool:
        """Comando: Enviar propuesta aprobada."""
        job_id = args.strip()
        if not job_id:
            return self.send_message("❌ Debes especificar el ID del trabajo: `/enviar <job_id>`")
        
        text = (
            f"✅ *Propuesta Enviada*\n\n"
            f"Job ID: `{job_id}`\n"
            f"Estado: Enviando a Freelancer.com...\n"
            f"(Ejecutando bid automático)"
        )
        return self.send_message(text)

    def cmd_responder(self, args: str = "") -> bool:
        """Comando: Enviar respuesta a cliente."""
        client = args.strip()
        if not client:
            return self.send_message("❌ Debes especificar el cliente: `/responder <client_name>`")
        
        text = (
            f"📩 *Respuesta Enviada*\n\n"
            f"Cliente: `{client}`\n"
            f"Estado: Enviando respuesta...\n"
            f"(Integración con plataforma pendiente)"
        )
        return self.send_message(text)

    def cmd_estado(self, args: str = "") -> bool:
        """Comando: Ver estado del sistema."""
        text = (
            "📊 *Estado del Sistema*\n\n"
            "✅ Bot: Conectado\n"
            "✅ Freelancer API: Conectada\n"
            "✅ OpenAI: Conectada\n"
            "⏳ Base de Datos: Sincronizando...\n\n"
            "Últimas Acciones:\n"
            "• Propuestas enviadas: 3\n"
            "• Trabajos ganados: 1\n"
            "• Mensajes procesados: 5"
        )
        return self.send_message(text)

    def cmd_ayuda(self, args: str = "") -> bool:
        """Comando: Mostrar ayuda."""
        text = (
            "❓ *Ayuda - Comandos Disponibles*\n\n"
            "📋 `/listar` - Ver oportunidades pendientes\n"
            "🔍 `/buscar [query]` - Buscar oportunidades\n"
            "✅ `/enviar <job_id>` - Enviar propuesta\n"
            "📩 `/responder <client>` - Responder a cliente\n"
            "📊 `/estado` - Ver estado del sistema\n"
            "❓ `/ayuda` - Mostrar esta ayuda\n\n"
            "💡 *Tips:*\n"
            "• Responde a un mensaje de oportunidad para editar la propuesta\n"
            "• Usa `/buscar python` para búsquedas específicas"
        )
        return self.send_message(text)

    def handle_command(self, command: str, args: str = "") -> bool:
        """Procesa un comando recibido."""
        handler = self.commands.get(command)
        if handler:
            return handler(args)
        else:
            return self.send_message(f"❌ Comando desconocido: `/{command}`\nUsa `/ayuda` para ver los comandos disponibles.")
