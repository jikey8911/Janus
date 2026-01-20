import logging
from infrastructure.celery_app import celery_app
from application.use_cases import ScanAndAnalyzeJobsUseCase

# Importamos las abstracciones de puertos
from domain.ports import JobRepository, UpworkPort, AIServicePort, NotificationPort

# --- DUMMY ADAPTERS (Para Sprint 2) ---
# En el Sprint 3 estos serán reemplazados por imports reales de infrastructure.adapters...

class DummyUpworkAdapter(UpworkPort):
    def search_jobs(self, query: str):
        logging.info(f"[Dummy] Buscando trabajos en Upwork con query: {query}")
        return [] # Retorna lista vacía por ahora

    def submit_proposal(self, job_id, content):
        logging.info(f"[Dummy] Enviando propuesta para {job_id}")
        return True

class DummyJobRepository(JobRepository):
    def save(self, job):
        logging.info(f"[Dummy] Guardando trabajo {job.upwork_id}")
        return job

    def get_by_upwork_id(self, upwork_id):
        return None

class DummyAIService(AIServicePort):
    def analyze_job(self, job):
        logging.info(f"[Dummy] Analizando trabajo {job.upwork_id}")
        return {"score": 85, "summary": "Looks good"}

    def suggest_reply(self, message):
        return "Respuesta sugerida"
        
    def generate_proposal_content(self, job) -> str:
        return "Contenido de propuesta dummy"

class DummyNotificationService(NotificationPort):
    def notify_opportunity(self, job, analysis):
        logging.info(f"[Dummy] Notificando oportunidad: {job.title}")
        return True

    def notify_message(self, message):
        logging.info(f"[Dummy] Notificando mensaje: {message}")
        return True

# --- TASKS ---

@celery_app.task(name="scan_jobs_task")
def scan_jobs_task(query: str = "(python OR automation)"):
    """
    Tarea periódica para buscar trabajos.
    Instancia los casos de uso con los adaptadores (dummies por ahora).
    """
    logging.info("Ejecutando Tarea: scan_jobs_task")
    
    # Inyección de dependencias (Manual por ahora)
    # Seleccionamos el adaptador según configuración o por defecto Freelancer (Prioritario Sprint 3)
    from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
    from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter
    
    # Podemos hacer esto configurable via ENV
    use_freelancer = True 
    
    if use_freelancer:
        platform_adapter = FreelancerAdapter()
    else:
        platform_adapter = UpworkAdapter()
        
    if use_freelancer:
        platform_adapter = FreelancerAdapter()
    else:
        platform_adapter = UpworkAdapter()
        
    # Inyección Real de Dependencias (Sprint 3 Complete)
    try:
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
        from infrastructure.adapters.analyzer.openai.adapter import OpenAIAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        
        job_repo = MongoJobRepository(connection_string=os.getenv("DATABASE_URL", "mongodb://localhost:27017/"))
        ai_service = OpenAIAdapter()
        notification_service = TelegramAdapter()
    except Exception as e:
        logging.error(f"Error loading adapters: {e}. Falling back to mocks.")
        job_repo = DummyJobRepository()
        ai_service = DummyAIService()
        notification_service = DummyNotificationService()
    
    use_case = ScanAndAnalyzeJobsUseCase(
        platform_port=platform_adapter,
        job_repo=job_repo,
        ai_port=ai_service,
        notification_port=notification_service
    )
    
    use_case = ScanAndAnalyzeJobsUseCase(
        platform_port=platform_adapter,
        job_repo=job_repo,
        ai_port=ai_service,
        notification_port=notification_service
    )
    
    use_case.execute(query=query)

@celery_app.task(name="poll_upwork_events_task")
def poll_upwork_events_task():
    """
    Tarea periódica (Pull) para consultar eventos en Upwork (Polling Strategy).
    Simula la consulta de nuevos mensajes o cambios de estado.
    """
    logging.info("Polling Upwork for new events...")
    
    # Dependencias
    # notification_service = DummyNotificationService() # Reemplazado por TelegramAdapter real si estuviera importado
    # relay_use_case = RelayClientMessageUseCase(notification_port=notification_service)

    # TODO: Implementar lógica de consulta a UpworkAdapter
    # updates = upwork_adapter.get_updates(since=last_checkpoint)
    # for update in updates:
    #     msg = ClientMessage(client_name=update.user, message_content=update.text, job_context=update.job_id)
    #     relay_use_case.execute(msg)
    pass
    logging.info("Tarea scan_jobs_task finalizada")

@celery_app.task(name="generate_proposal_task")
def generate_proposal_task(job_id: str):
    """
    Tarea para generar una propuesta para un trabajo específico.
    HU 2.2
    """
    logging.info(f"Generating proposal for Job ID: {job_id}")
    
    # Inyección de Dependencias
    try:
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository, MongoProposalRepository
        from infrastructure.adapters.analyzer.openai.adapter import OpenAIAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from application.use_cases import GenerateProposalUseCase
        
        db_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017/")
        job_repo = MongoJobRepository(connection_string=db_url)
        proposal_repo = MongoProposalRepository(connection_string=db_url)
        ai_service = OpenAIAdapter()
        notification_service = TelegramAdapter()
        
        use_case = GenerateProposalUseCase(
            job_repo=job_repo,
            proposal_repo=proposal_repo,
            ai_port=ai_service,
            notification_port=notification_service
        )
        
        use_case.execute(job_upwork_id=job_id)
        
    except Exception as e:
        logging.error(f"Error in generate_proposal_task: {e}")
