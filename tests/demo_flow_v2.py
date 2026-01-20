import sys
import os
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

import logging
from domain.entities import JobOffer
# IMPORTING THE CLEAN ADAPTER
from infrastructure.adapters.simple_telegram import TelegramAdapter

logging.basicConfig(level=logging.INFO)

def run_demo():
    print("🚀 Iniciando Demo de Flujo Completo Janus V2.1 (V2)")
    
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
    
    print("3. Enviando notificación a Telegram (Clean Adapter)...")
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
