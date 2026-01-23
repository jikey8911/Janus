from celery import shared_task
import logging
import asyncio

# Adaptadores
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter
from infrastructure.adapters.analyzer.groq.adapter import GroqAdapter
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from infrastructure.adapters.persistence.mongodb.adapter import MongoProposalRepository, MongoJobRepository, MongoEventCheckpointRepository
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancias de adaptadores principal (Freelancer)
try:
    freelancer_adapter = FreelancerAdapter()
    upwork_adapter = UpworkAdapter() # Se mantiene para compatibilidad de infraestructura
    ai_adapter = GroqAdapter()
    telegram_adapter = TelegramAdapter()
except Exception as e:
    logger.error(f"Error inicializando adaptadores en worker: {e}")

@shared_task(name="scan_jobs_task")
def scan_jobs_task(query: str = "", limit: int = 10):
    logger.info(f"🕒 Ejecutando Tarea: Buscando {limit} ofertas recientes (query: '{query}')...")
    
    try:
        # Importar adaptadores y casos de uso
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        from infrastructure.adapters.analyzer.groq.adapter import GroqAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
        from application.use_cases import ScanAndAnalyzeJobsUseCase
        
        # Instanciar adaptadores
        platform_adapter = FreelancerAdapter()
        ai_adapter = GroqAdapter()
        notification_adapter = TelegramAdapter()
        job_repo = MongoJobRepository()
        proposal_repo = MongoProposalRepository()
        
        # Ejecutar caso de uso completo
        use_case = ScanAndAnalyzeJobsUseCase(
            platform_port=platform_adapter,
            job_repo=job_repo,
            ai_port=ai_adapter,
            notification_port=notification_adapter,
            proposal_repo=proposal_repo
        )
        
        use_case.execute(query, limit=limit)
        logger.info("✅ Tarea de escaneo completada exitosamente.")
        
    except Exception as e:
        error_msg = f"❌ Error CRÍTICO en scan_jobs_task: {e}"
        logger.error(error_msg)
        try:
            from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
            TelegramAdapter().notify_error(error_msg)
        except:
            pass
        import traceback
        logger.error(traceback.format_exc())

@shared_task(name="periodic_quick_scan_task")
def periodic_quick_scan_task():
    """
    Tarea periódica: Obtiene solo la oferta más reciente (limit=1).
    Solo se guarda y notifica si el score de IA es >= 80 (aprobación automática).
    """
    logger.info("🕒 Ejecutando Escaneo Rápido Periódico (1 Job, Score > 80)...")
    try:
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        from infrastructure.adapters.analyzer.groq.adapter import GroqAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
        from application.use_cases import ScanAndAnalyzeJobsUseCase
        
        use_case = ScanAndAnalyzeJobsUseCase(
            platform_port=FreelancerAdapter(),
            job_repo=MongoJobRepository(),
            ai_port=GroqAdapter(),
            notification_port=TelegramAdapter(),
            proposal_repo=MongoProposalRepository()
        )
        
        # Limit=1, Min_Score=80 (Solo lo mejor de lo mejor), query vacío para amplitud
        use_case.execute(query="", limit=1, min_score=80)
        logger.info("✅ Escaneo periódico completado.")
        
    except Exception as e:
        error_msg = f"❌ Error en periodic_quick_scan_task: {e}"
        logger.error(error_msg)
        try:
            from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
            TelegramAdapter().notify_error(error_msg)
        except:
            pass

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
@shared_task(name="monitor_notifications_task")
def monitor_notifications_task(platform: str = "freelancer"):
    """
    Tarea periódica (cada 5 min) para monitorear notificaciones de plataforma.
    """
    logger.info(f"🕒 Ejecutando Monitoreo de Notificaciones para '{platform}'...")
    try:
        from application.award_and_message_use_cases import MonitorNotificationsUseCase
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from infrastructure.adapters.persistence.mongodb.adapter import MongoEventCheckpointRepository
        
        # En una arquitectura real, usaríamos la Factoría
        from infrastructure.factories import PlatformFactory
        platform_adapter = PlatformFactory.get_adapter(platform)
        
        use_case = MonitorNotificationsUseCase(
            platform_port=platform_adapter,
            checkpoint_repo=MongoEventCheckpointRepository(),
            notification_port=TelegramAdapter()
        )
        
        use_case.execute(platform)
        logger.info(f"✅ Monitoreo de '{platform}' completado.")
        
    except Exception as e:
        logger.error(f"❌ Error en monitor_notifications_task: {e}")
