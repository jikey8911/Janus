"""
Script de verificación para validación de propuestas via Telegram.
Prueba el flujo completo: Generar propuesta → Enviar a Telegram con botones inline
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from dotenv import load_dotenv
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

def main():
    print("=" * 60)
    print("Verificación: Validación de Propuestas via Telegram")
    print("=" * 60)
    
    # Verificar credenciales
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados")
        return
    
    print(f"\n✅ Credenciales encontradas")
    print(f"   Bot Token: {bot_token[:10]}...")
    print(f"   Chat ID: {chat_id}")
    
    # Instanciar adapter
    print("\n[1/3] Inicializando TelegramAdapter...")
    adapter = TelegramAdapter()
    
    # Crear propuesta de prueba
    print("\n[2/3] Creando propuesta de prueba...")
    job_title = "Senior Python Developer - FastAPI & React"
    proposal_content = """
Hello! I'm excited about this opportunity.

I have 5+ years of experience with:
- Python FastAPI development
- React.js frontend
- PostgreSQL databases
- Docker & CI/CD pipelines

I can deliver a production-ready MVP within 4 weeks, including:
✅ Backend API with authentication
✅ React frontend with TypeScript
✅ Database schema & migrations
✅ Docker deployment setup
✅ Basic CI/CD pipeline

Let's discuss the specific requirements in detail.

Best regards,
[Your Name]
    """.strip()
    
    # Enviar propuesta con botones
    print("\n[3/3] Enviando propuesta a Telegram con botones inline...")
    try:
        success = adapter.send_proposal_for_validation(
            job_title=job_title,
            proposal_content=proposal_content,
            proposal_id=12345,
            job_id="test_job_001",
            analysis_score=85
        )
        
        if success:
            print("✅ Propuesta enviada exitosamente a Telegram")
            print("\n📱 Revisa tu chat de Telegram para ver:")
            print("   - Propuesta formateada")
            print("   - Botones: ✅ Aprobar | ❌ Rechazar | ✏️ Editar | 📊 Ver Análisis")
        else:
            print("❌ Error enviando propuesta")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETA")
    print("=" * 60)

if __name__ == "__main__":
    main()
