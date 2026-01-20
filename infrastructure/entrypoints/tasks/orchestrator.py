import json
from tasks.celery_app import celery_app
from app.core.upwork_service import UpworkService
from app.core.ai_service import AIService
from app.core.telegram_service import TelegramService
from app.db.session import SessionLocal
from app.db.models import JobOffer

@celery_app.task(name="tasks.orchestrator.scan_and_notify")
def scan_and_notify():
    upwork_ws = UpworkService()
    ai_ws = AIService()
    telegram_ws = TelegramService()
    db = SessionLocal()
    
    try:
        jobs = upwork_ws.search_jobs()
        for job in jobs:
            # Verificar si ya existe
            exists = db.query(JobOffer).filter(JobOffer.upwork_id == job['id']).first()
            if not exists:
                # Guardar nueva oferta
                new_job = JobOffer(
                    upwork_id=job['id'],
                    title=job['title'],
                    description=job['snippet'],
                    budget=job.get('budget', 'N/A')
                )
                db.add(new_job)
                db.commit()
                db.refresh(new_job)
                
                # Analizar con IA
                analysis_raw = ai_ws.analyze_job_and_generate_proposal(new_job.title, new_job.description)
                analysis = json.loads(analysis_raw)
                
                # Notificar por Telegram
                telegram_ws.send_opportunity_with_proposal(new_job, analysis)
                
    finally:
        db.close()
