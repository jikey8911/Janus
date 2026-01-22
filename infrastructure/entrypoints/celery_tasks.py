from celery import shared_task
import logging
import asyncio

# Adaptadores (Lazy Imports para evitar ciclos si es necesario, pero mejor arriba si están limpios)
from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter
from infrastructure.adapters.analyzer.openai.adapter import OpenAIAdapter
# from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter # Usaremos la version limpia V2 si aplica
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter # Usar simple_telegram si sigue fallando
from infrastructure.adapters.persistence.mongodb.adapter import MongoProposalRepository, MongoJobRepository, MongoEventCheckpointRepository
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancias de adaptadores (Singleton-ish para el worker)
# En produccion, inyeccion de dependencias mas robusta
try:
    upwork_adapter = UpworkAdapter()
    # openai_adapter = OpenAIAdapter() # Comentado si no se usa aun o si da error
    # telegram_adapter = TelegramAdapter()
    
    # Repositorios
    # job_repo = MongoJobRepository()
    # proposal_repo = MongoProposalRepository()
except Exception as e:
    logger.error(f"Error inicializando adaptadores en worker: {e}")

@shared_task(name="scan_jobs_task")
def scan_jobs_task(query: str = "Python"):
    logger.info(f"🕒 Ejecutando Tarea: Buscando ofertas para '{query}'...")
    
    try:
        # Importar adaptadores y casos de uso
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        from infrastructure.adapters.analyzer.gemini.adapter import GeminiAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
        from application.use_cases import ScanAndAnalyzeJobsUseCase
        
        # Instanciar adaptadores
        platform_adapter = FreelancerAdapter()
        ai_adapter = GeminiAdapter()
        notification_adapter = TelegramAdapter()
        job_repo = MongoJobRepository()
        
        # Ejecutar caso de uso completo
        use_case = ScanAndAnalyzeJobsUseCase(
            platform_port=platform_adapter,
            job_repo=job_repo,
            ai_port=ai_adapter,
            notification_port=notification_adapter
        )
        
        use_case.execute(query)
        logger.info("✅ Tarea de escaneo completada exitosamente.")
        
    except Exception as e:
        logger.error(f"❌ Error CRÍTICO en scan_jobs_task: {e}")
        import traceback
        logger.error(traceback.format_exc())

@shared_task(name="poll_upwork_events_task")
def poll_upwork_events_task():
    logger.info("🔄 Polling Upwork Events (Cada 60s)...")
    # Implementar logica real de polling incremental usando Checkpoints
    pass

@shared_task(name="generate_proposal_task")
def generate_proposal_task(job_id: str):
    logger.info(f"🤖 Generando propuesta para Job ID: {job_id}")
    # 1. Recuperar Job de DB o API
    # 2. Analizar con IA
    # 3. Generar propuesta
    # 4. Guardar y Notificar
    pass
