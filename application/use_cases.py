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

    def execute(self, query: str = "(python OR automation OR ai)", limit: int = 10, min_score: int = 0):
        logging.info(f"Iniciando búsqueda de trabajos con query: '{query}', limit: {limit}, min_score: {min_score}")
        try:
            # Pasar el límite al adaptador si lo soporta (Freelancer lo hace ahora)
            if hasattr(self.platform_port, 'search_jobs'):
                import inspect
                sig = inspect.signature(self.platform_port.search_jobs)
                if 'limit' in sig.parameters:
                    jobs = self.platform_port.search_jobs(query, limit=limit)
                else:
                    jobs = self.platform_port.search_jobs(query)[:limit]
            else:
                jobs = []
            
            logging.info(f"Se encontraron {len(jobs)} ofertas en plataforma.")
        except Exception as e:
            logging.error(f"Error buscando trabajos en plataforma: {e}")
            return

        # Importar generador de reportes
        from infrastructure.utils.report_generator import MarkdownReportGenerator
        report_gen = MarkdownReportGenerator()

        for job in jobs:
            try:
                # Primero verificamos si ya existe para no analizar dos veces lo mismo
                existing_job = self.job_repo.get_by_external_id(job.external_id)
                if existing_job:
                    logging.debug(f"Oferta ya existe: {job.external_id}")
                    continue

                logging.info(f"Nueva oferta encontrada: {job.title} ({job.external_id}). Analizando...")
                
                # 1. Análisis con IA ANTES de guardar (según solicitud del usuario)
                analysis = self.ai_port.analyze_job(job)
                score = analysis.get('score', 0)
                logging.info(f"Análisis completado para {job.external_id}: Score {score}")

                # 2. Filtro de "Aprobación" (Solo si supera el min_score)
                if score < min_score:
                    logging.info(f"Oferta {job.external_id} rechazada por bajo score ({score} < {min_score})")
                    continue

                # 3. Guardar solo si aprobó el filtro
                saved_job = self.job_repo.save(job)
                
                # 4. Generar reporte markdown
                try:
                    report_path = report_gen.generate_job_analysis_report(saved_job, analysis)
                    logging.info(f"Reporte generado: {report_path}")
                except Exception as report_err:
                    logging.error(f"Error generando reporte markdown: {report_err}")
                
                # 5. Notificar oportunidad a Telegram
                self.notification_port.notify_opportunity(saved_job, analysis)
                    
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

    def execute(self, job_external_id: str) -> Optional[Proposal]:
        logging.info(f"Generando propuesta para el trabajo: {job_external_id}")
        try:
            # Intentar obtener job del repo, si falla (por DB), podríamos intentar fallback si tuviéramos cache
            try:
                job = self.job_repo.get_by_external_id(job_external_id)
            except Exception as e:
                logging.warning(f"Error accediendo a DB para obtener job: {e}. No se puede proceder sin job.")
                return None

            if not job:
                logging.error(f"Trabajo no encontrado en DB: {job_external_id}")
                return None

            # Generar análisis primero para obtener score y monto sugerido
            analysis = self.ai_port.analyze_job(job)
            score = analysis.get('score', 0)
            suggested_bid = analysis.get('suggested_bid')
            
            # Si no hay monto sugerido por la IA, usar el mínimo del trabajo
            if not suggested_bid:
                suggested_bid = job.min_amount or 0
            
            # Generar contenido de propuesta
            content = self.ai_port.generate_proposal_content(job)
            
            # Crear propuesta en estado draft
            proposal = Proposal(
                job_offer_id=job.id if job.id else 0,
                content=content,
                status="draft",
                bid_amount=float(suggested_bid) if suggested_bid else None,
                currency=job.currency
            )
            
            # Guardado resiliente: si la DB falla, seguimos adelante asignando un ID temporal
            saved_proposal = proposal
            try:
                saved_proposal = self.proposal_repo.save(proposal)
                logging.info(f"Propuesta guardada en DB: {saved_proposal.id}")
            except Exception as e:
                import time
                saved_proposal.id = int(time.time())
                logging.warning(f"No se pudo guardar la propuesta en DB: {e}. Usando ID temporal {saved_proposal.id}")
            
            # Enviar a Telegram para validación
            self.notification_port.send_proposal_for_validation(
                job_title=job.title,
                proposal_content=saved_proposal.content,
                proposal_id=saved_proposal.id,
                job_id=job.external_id,
                analysis_score=score,
                bid_amount=saved_proposal.bid_amount,
                currency=saved_proposal.currency
            )
            
            return saved_proposal

        except Exception as e:
            logging.error(f"Error crítico generando propuesta para {job_upwork_id}: {e}")
            return None

class SubmitProposalUseCase:
    def __init__(
        self, 
        platform_port: FreelancePlatformPort, 
        proposal_repo: ProposalRepository,
        notification_port: NotificationPort
    ):
        self.platform_port = platform_port
        self.proposal_repo = proposal_repo
        self.notification_port = notification_port

    def execute(self, job_external_id: str, content: str):
        success = self.platform_port.submit_proposal(job_external_id, content)
        if success:
            # Aquí se guardaría la propuesta en el repo si fuera necesario
            self.notification_port.notify_message(f"Propuesta enviada con éxito para {job_external_id}")
        return success
