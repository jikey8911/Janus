import logging
from typing import Optional
from domain.ports import JobRepository, ProposalRepository, FreelancePlatformPort, AIServicePort, NotificationPort
from domain.entities import JobOffer, Proposal

class ScanAndAnalyzeJobsUseCase:
    def __init__(
        self,
        platform_port: FreelancePlatformPort,
        job_repo: JobRepository,
        ai_port: AIServicePort,
        notification_port: NotificationPort
    ):
        self.platform_port = platform_port
        self.job_repo = job_repo
        self.ai_port = ai_port
        self.notification_port = notification_port

    def execute(self, query: str = "(python OR automation OR ai)"):
        logging.info(f"Iniciando búsqueda de trabajos con query: '{query}'")
        try:
            jobs = self.platform_port.search_jobs(query)
            logging.info(f"Se encontraron {len(jobs)} ofertas en plataforma.")
        except Exception as e:
            logging.error(f"Error buscando trabajos en plataforma: {e}")
            return

        # Importar generador de reportes
        from infrastructure.utils.report_generator import MarkdownReportGenerator
        report_gen = MarkdownReportGenerator()

        for job in jobs:
            try:
                existing_job = self.job_repo.get_by_upwork_id(job.external_id)
                if not existing_job:
                    logging.info(f"Nueva oferta encontrada: {job.title} ({job.external_id})")
                    saved_job = self.job_repo.save(job)
                    
                    try:
                        # Análisis con IA
                        analysis = self.ai_port.analyze_job(saved_job)
                        logging.info(f"Análisis completado para {job.external_id}: Score {analysis.get('score', 0)}")
                        
                        # Generar reporte markdown
                        try:
                            report_path = report_gen.generate_job_analysis_report(saved_job, analysis)
                            logging.info(f"Reporte generado: {report_path}")
                        except Exception as report_err:
                            logging.error(f"Error generando reporte markdown: {report_err}")
                        
                        # Notificar oportunidad
                        self.notification_port.notify_opportunity(saved_job, analysis)
                    except Exception as e:
                        logging.error(f"Error analizando/notificando oferta {job.external_id}: {e}")
                else:
                    logging.debug(f"Oferta ya existe: {job.external_id}")
                    
            except Exception as e:
                logging.error(f"Error procesando oferta {job.external_id}: {e}")

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

            # Generar análisis primero para obtener score
            analysis = self.ai_port.analyze_job(job)
            score = analysis.get('score', 0)
            
            # Generar contenido de propuesta
            content = self.ai_port.generate_proposal_content(job)
            
            # Crear propuesta en estado draft
            proposal = Proposal(
                job_offer_id=job.id if job.id else 0,
                content=content,
                status="draft"
            )
            
            saved_proposal = self.proposal_repo.save(proposal)
            logging.info(f"Propuesta generada y guardada: {saved_proposal.id}")
            
            # Enviar a Telegram para validación con botones inline
            self.notification_port.send_proposal_for_validation(
                job_title=job.title,
                proposal_content=saved_proposal.content,
                proposal_id=saved_proposal.id,
                job_id=job.external_id,
                analysis_score=score
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
