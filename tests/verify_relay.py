from dotenv import load_dotenv
load_dotenv()

from domain.entities import ClientMessage
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from application.relay_use_case import RelayClientMessageUseCase

def verify_relay():
    print("Testing RelayClientMessageUseCase...")
    
    # 1. Instantiate Adapter (Loads env vars)
    adapter = TelegramAdapter()
    if not adapter.chat_id:
        print("ERROR: Chat ID not configured in .env")
        return

    # 2. Instantiate Use Case
    use_case = RelayClientMessageUseCase(header_adapter=adapter) # Error intencionado para corregir en codigo real si nombre param es distinto

    # 2.1 Correction: The use case expects 'notification_port'
    use_case = RelayClientMessageUseCase(notification_port=adapter)

    # 3. Create Dummy Message
    msg = ClientMessage(
        client_name="Test Client (Verify Script)",
        message_content="Hello, this is a test message from the relay system.",
        job_context="Verification Job #123"
    )

    # 4. Execute
    print(f"Sending message to Chat ID: {adapter.chat_id}")
    use_case.execute(msg)
    print("Execution finished. Check your Telegram!")

if __name__ == "__main__":
    verify_relay()
