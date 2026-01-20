import sys
import os
sys.path.append(os.getcwd()) # Ensure root dir is in path

from dotenv import load_dotenv
load_dotenv()

import logging
from domain.entities import JobOffer
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter

# Setup Logger
logging.basicConfig(level=logging.INFO)

def run_demo():
    print("🚀 Iniciando Demo de Flujo Completo Janus V2.1")
    
    # 1. Simular una Oferta de Trabajo detectada
    print("1. Simulando detección de Job...")
    job = JobOffer(
        upwork_id="TEST_JOB_999",
        title="Python Developer Needed (Demo)",
        description="Looking for an expert to verify Janus Flow. Pays well.",
        budget="$1000",
        category="Software Development",
        status="pending"
    )
    
    # 2. Simular Análisis IA (Mock)
    print("2. Simulando análisis IA...")
    analysis = {
        "score": 95,
        "reasoning": "This job matches perfectly with Janus capabilities."
    }
    
    # 3. Enviar Notificación (Telegram)
    print("3. Enviando notificación a Telegram...")
    adapter = TelegramAdapter()
    print(f"DEBUG: Chat ID loaded: {adapter.chat_id}") 
    
    success = adapter.notify_opportunity(job, analysis)
    
    if success:
        print("\n✅ Notificación enviada con éxito.")
        print("👉 POR FAVOR, REVISA TU TELEGRAM.")
    else:
        print("❌ Falló el envío de notificación.")

if __name__ == "__main__":
    run_demo()
