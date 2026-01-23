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
                # Primero verificamos si ya existe
                existing_job = self.job_repo.get_by_external_id(job.external_id)
                
                # Si existe, solo continuamos si ya tiene análisis (para no repetir)
                # Si existe NO tiene análisis, procedemos a analizarlo
                if existing_job and getattr(existing_job, 'analysis', None):
                    logging.info(f"Omitiendo: Oferta {job.external_id} ya analizada en DB.")
                    continue
                
                logging.info(f"Procesando oferta: {job.title} ({job.external_id}). Analizando...")
                
                # 1. Análisis con IA
                analysis = self.ai_port.analyze_job(job)
                score = analysis.get('score', 0)
                
                # Fallback si el score es 0 pero hay razonamiento (posible error de parsing JSON en IA)
                if score == 0 and "reasoning" in analysis:
                    logging.warning(f"IA devolvió score 0 o error: {analysis.get('reasoning')}")
                    # En este punto, no saltamos el guardado para que el usuario vea el error
                
                logging.info(f"Análisis completado para {job.external_id}: Score {score}")

                # 2. Filtro de "Aprobación" (Solo si supera el min_score o si es un error de IA permitimos pasar para debugging)
                if score < min_score and score != 0:
                    logging.info(f"Oferta {job.external_id} rechazada por bajo score ({score} < {min_score})")
                    continue

                # 3. Guardar solo si aprobó el filtro
                job.analysis = analysis
                saved_job = self.job_repo.save(job)
                logging.info(f"Oferta {job.external_id} guardada con su análisis.")
                
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
            # Usamos el external_id del trabajo para facilitar el envío a plataforma posterior
            proposal = Proposal(
                job_offer_id=job.external_id,
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
            logging.error(f"Error crítico generando propuesta para {job_external_id}: {e}")
            return None

class SubmitProposalUseCase:
    def __init__(
        self, 
        proposal_repo: ProposalRepository,
        notification_port: NotificationPort,
        job_repo: JobRepository,
        platform_factory=None # Inyectar factoría o manejar adaptadores
    ):
        self.proposal_repo = proposal_repo
        self.notification_port = notification_port
        self.job_repo = job_repo
        self.platform_factory = platform_factory

    def execute(self, proposal_id: int):
        logging.info(f"Iniciando envío real de propuesta ID: {proposal_id}")
        try:
            # 1. Obtener propuesta
            proposal = self.proposal_repo.get_by_id(proposal_id)
            if not proposal:
                logging.error(f"Propuesta {proposal_id} no encontrada.")
                return False

            # 2. Determinar plataforma
            platform_name = getattr(proposal, 'platform', 'freelancer')
            
            # Obtener adaptador desde la factoría si está disponible
            if self.platform_factory:
                platform_adapter = self.platform_factory.get_adapter(platform_name)
            else:
                # Fallback o inyección directa si se prefiere
                logging.error("PlatformFactory no disponible en SubmitProposalUseCase.")
                return False

            # 3. Obtener trabajo relacionado (opcional para el envío si ya tenemos ID externo)
            job_id = str(proposal.job_offer_id)
            job = self.job_repo.get_by_external_id(job_id)

            # 4. Enviar a plataforma
            success = platform_adapter.submit_proposal(
                job_id=job_id, 
                content=proposal.content,
                amount=proposal.bid_amount
            )
            
            if success:
                # 4. Actualizar estado
                proposal.status = "submitted"
                from datetime import datetime
                proposal.submitted_at = datetime.now()
                self.proposal_repo.save(proposal)
                nombre_trabajo = job.title if job else "desconocido"
                self.notification_port.notify_message(f"✅ Propuesta enviada con éxito para el trabajo: {nombre_trabajo} (ID: {job_id})")
            else:
                nombre_trabajo = job.title if job else "desconocido"
                self.notification_port.notify_message(f"❌ Error al enviar la propuesta para el trabajo: {nombre_trabajo} (ID: {job_id})")
            
            return success
        except Exception as e:
            logging.error(f"Error en SubmitProposalUseCase: {e}")
            return False

class UpdateProposalUseCase:
    def __init__(self, proposal_repo: ProposalRepository, notification_port: NotificationPort):
        self.proposal_repo = proposal_repo
        self.notification_port = notification_port

    def execute(self, proposal_id: int, new_content: str, new_amount: Optional[float] = None) -> bool:
        logging.info(f"Actualizando propuesta ID: {proposal_id}")
        try:
            proposal = self.proposal_repo.get_by_id(proposal_id)
            if not proposal:
                return False
            
            proposal.content = new_content
            if new_amount is not None:
                proposal.bid_amount = new_amount
            
            self.proposal_repo.save(proposal)
            self.notification_port.notify_message(f"📝 Propuesta {proposal_id} actualizada correctamente.")
            return True
        except Exception as e:
            logging.error(f"Error actualizando propuesta: {e}")
            return False

class RejectProposalUseCase:
    def __init__(self, proposal_repo: ProposalRepository, notification_port: NotificationPort):
        self.proposal_repo = proposal_repo
        self.notification_port = notification_port

    def execute(self, proposal_id: int) -> bool:
        logging.info(f"Rechazando propuesta ID: {proposal_id}")
        try:
            proposal = self.proposal_repo.get_by_id(proposal_id)
            if not proposal:
                return False
            
            proposal.status = "rejected"
            self.proposal_repo.save(proposal)
            self.notification_port.notify_message(f"🚫 Propuesta {proposal_id} marcada como rechazada.")
            return True
        except Exception as e:
            logging.error(f"Error rechazando propuesta: {e}")
            return False
