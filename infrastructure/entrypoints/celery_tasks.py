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
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
        
        # Instanciar adaptador (intentará leer ENV valid token)
        adapter = FreelancerAdapter()
        repo = MongoJobRepository()
        
        jobs = adapter.search_jobs(query)
        
        if not jobs:
            logger.info("⚠️ No se encontraron ofertas (o error en API).")
            return
            
        logger.info(f"✅ Encontradas {len(jobs)} ofertas. Guardando...")
        
        saved_count = 0
        for job in jobs:
            try:
                repo.save(job)
                saved_count += 1
            except Exception as save_err:
                logger.error(f"Error guardando job: {save_err}")
                
        logger.info(f"💾 Guardadas {saved_count}/{len(jobs)} ofertas en MongoDB.")
        
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
