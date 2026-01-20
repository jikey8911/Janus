import logging
from typing import Optional
from domain.ports import JobRepository, ProposalRepository, UpworkPort, AIServicePort, NotificationPort
from domain.entities import JobOffer, Proposal

class ScanAndAnalyzeJobsUseCase:
    def __init__(
        self, 
        upwork_port: UpworkPort, 
        job_repo: JobRepository, 
        ai_port: AIServicePort, 
        notification_port: NotificationPort
    ):
        self.upwork_port = upwork_port
        self.job_repo = job_repo
        self.ai_port = ai_port
        self.notification_port = notification_port

    def execute(self, query: str = "(python OR automation OR ai)"):
        logging.info(f"Iniciando búsqueda de trabajos con query: '{query}'")
        try:
            jobs = self.upwork_port.search_jobs(query)
            logging.info(f"Se encontraron {len(jobs)} ofertas en Upwork.")
        except Exception as e:
            logging.error(f"Error buscando trabajos en Upwork: {e}")
            return

        for job in jobs:
            try:
                existing_job = self.job_repo.get_by_upwork_id(job.upwork_id)
                if not existing_job:
                    logging.info(f"Nueva oferta encontrada: {job.title} ({job.upwork_id})")
                    saved_job = self.job_repo.save(job)
                    
                    try:
                        analysis = self.ai_port.analyze_job(saved_job)
                        logging.info(f"Análisis completado para {job.upwork_id}")
                        self.notification_port.notify_opportunity(saved_job, analysis)
                    except Exception as e:
                        logging.error(f"Error analizando/notificando oferta {job.upwork_id}: {e}")
                else:
                    logging.debug(f"Oferta ya existe: {job.upwork_id}")
                    
            except Exception as e:
                logging.error(f"Error procesando oferta {job.upwork_id}: {e}")

class GenerateProposalUseCase:
    def __init__(
        self,
        job_repo: JobRepository,
        proposal_repo: ProposalRepository,
        ai_port: AIServicePort,
        notification_port: NotificationPort
    ):
        self.job_repo = job_repo
        self.proposal_repo = proposal_repo
        self.ai_port = ai_port
        self.notification_port = notification_port

    def execute(self, job_upwork_id: str) -> Optional[Proposal]:
        logging.info(f"Generando propuesta para el trabajo: {job_upwork_id}")
        try:
            job = self.job_repo.get_by_upwork_id(job_upwork_id)
            if not job:
                logging.error(f"Trabajo no encontrado: {job_upwork_id}")
                return None

            content = self.ai_port.generate_proposal_content(job)
            
            # Asumimos que si no tiene ID aún, es 0 o None, pero el repo lo manejará.
            # En entities.py Proposal.id es Optional[int].
            proposal = Proposal(
                job_offer_id=job.id if job.id else 0, # Idealmente job debería tener ID si viene del repo
                content=content,
                status="draft"
            )
            
            saved_proposal = self.proposal_repo.save(proposal)
            logging.info(f"Propuesta generada y guardada: {saved_proposal.id}")
            
            self.notification_port.notify_message(
                f"Propuesta generada (ID: {saved_proposal.id}) para oferta {job_upwork_id}"
            )
            
            return saved_proposal

        except Exception as e:
            logging.error(f"Error generando propuesta para {job_upwork_id}: {e}")
            return None

class SubmitProposalUseCase:
    def __init__(
        self, 
        upwork_port: UpworkPort, 
        proposal_repo: ProposalRepository,
        notification_port: NotificationPort
    ):
        self.upwork_port = upwork_port
        self.proposal_repo = proposal_repo
        self.notification_port = notification_port

    def execute(self, job_upwork_id: str, content: str):
        success = self.upwork_port.submit_proposal(job_upwork_id, content)
        if success:
            # Aquí se guardaría la propuesta en el repo si fuera necesario
            self.notification_port.notify_message(f"Propuesta enviada con éxito para {job_upwork_id}")
        return success
