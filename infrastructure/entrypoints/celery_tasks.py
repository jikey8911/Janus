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
    upwork_adapter = DummyUpworkAdapter()
    job_repo = DummyJobRepository()
    ai_service = DummyAIService()
    notification_service = DummyNotificationService()
    
    use_case = ScanAndAnalyzeJobsUseCase(
        upwork_port=upwork_adapter,
        job_repo=job_repo,
        ai_port=ai_service,
        notification_port=notification_service
    )
    
    use_case.execute(query=query)
    logging.info("Tarea scan_jobs_task finalizada")

@celery_app.task(name="generate_proposal_task")
def generate_proposal_task(job_id: str):
    """
    Tarea para generar una propuesta asíncronamente (ej: disparada por webhook).
    NOTA: Para que funcione real, necesitamos el adapter real que saque el job de la DB real.
    """
    logging.info(f"Ejecutando Tarea: generate_proposal_task para job {job_id}")
    # Pendiente conectar con GenerateProposalUseCase cuando tengamos DB real
    pass
