"""
Casos de Uso para Gestión de Adjudicaciones y Mensajes de Clientes
"""
import logging
from typing import Optional
from datetime import datetime
from domain.ports import (
    ProposalRepository,
    JobRepository,
    NotificationPort,
    AIServicePort,
    PlatformEventPort
)
from domain.entities import ClientMessage, Proposal, JobOffer

logger = logging.getLogger(__name__)


class HandleProposalAwardedUseCase:
    """
    Caso de uso para manejar la adjudicación de una propuesta.
    Transiciona el estado a producción y notifica al usuario.
    """
    
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        job_repo: JobRepository,
        notification_port: NotificationPort
    ):
        self.proposal_repo = proposal_repo
        self.job_repo = job_repo
        self.notification_port = notification_port
    
    def execute(self, proposal_id: int, job_external_id: str):
        """
        Ejecuta el flujo de adjudicación.
        
        Args:
            proposal_id: ID interno de la propuesta
            job_external_id: ID del trabajo en la plataforma
        """
        try:
            # 1. Obtener propuesta
            # proposal = self.proposal_repo.get_by_id(proposal_id)
            # TODO: Implementar get_by_id en repository
            
            # 2. Actualizar estado a 'awarded'
            # self.proposal_repo.update_status(proposal_id, 'awarded')
            logger.info(f"Proposal {proposal_id} marked as awarded")
            
            # 3. Obtener detalles del trabajo
            job = self.job_repo.get_by_external_id(job_external_id)
            
            # 4. Notificar adjudicación por Telegram
            if job:
                self.notification_port.notify_message(
                    f"🎉 **¡PROYECTO ADJUDICADO!**\n\n"
                    f"**Proyecto:** {job.title}\n"
                    f"**Presupuesto:** {job.budget}\n"
                    f"**ID Propuesta:** {proposal_id}\n\n"
                    f"**Estado:** Transicionando a producción...\n\n"
                    f"_El proyecto ha sido adjudicado exitosamente._"
                )
            
            # 5. Transición a producción
            # self.proposal_repo.update_status(proposal_id, 'in_production')
            logger.info(f"Proposal {proposal_id} transitioned to in_production")
            
            # 6. Aquí se podría iniciar el flujo de producción (Sprint 6)
            # start_production_workflow(proposal_id, job)
            
        except Exception as e:
            logger.error(f"Error handling proposal award: {e}")
            raise


class HandleClientMessageUseCase:
    """
    Caso de uso para manejar mensajes de clientes.
    Genera respuesta con IA y envía a Telegram para aprobación.
    """
    
    def __init__(
        self,
        ai_port: AIServicePort,
        notification_port: NotificationPort
    ):
        self.ai_port = ai_port
        self.notification_port = notification_port
    
    def execute(self, message_data: dict):
        """
        Procesa un mensaje del cliente.
        
        Args:
            message_data: Dict con datos del mensaje
                {
                    'from': nombre del cliente,
                    'text': contenido del mensaje,
                    'context': contexto del proyecto,
                    'proposal_id': ID de la propuesta
                }
        """
        try:
            # 1. Crear entidad ClientMessage
            message = ClientMessage(
                client_name=message_data.get('from', 'Cliente'),
                message_content=message_data.get('text', ''),
                job_context=message_data.get('context', 'Proyecto freelance')
            )
            
            logger.info(f"Processing message from {message.client_name}")
            
            # 2. Generar respuesta sugerida con IA
            suggested_reply = self.ai_port.suggest_reply(message)
            logger.info(f"AI generated reply: {suggested_reply[:50]}...")
            
            # 3. Enviar a Telegram para aprobación
            proposal_id = message_data.get('proposal_id', 'unknown')
            
            notification_message = f"""📬 **MENSAJE DEL CLIENTE**

**Cliente:** {message.client_name}
**Propuesta ID:** {proposal_id}

**Cliente dice:**
"{message.message_content}"

---

**Respuesta sugerida por IA:**
"{suggested_reply}"

---
_Usa los botones para aprobar o editar la respuesta._
"""
            
            # TODO: Implementar send_message_for_approval con inline keyboard
            self.notification_port.notify_message(notification_message)
            
            logger.info(f"Message sent to Telegram for approval")
            
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            raise


class MonitorProposalsUseCase:
    """
    Caso de uso para monitorear propuestas activas.
    Usado por Celery tasks para polling (Upwork) o como fallback (Freelancer).
    """
    
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        platform_port: PlatformEventPort,
        award_use_case: HandleProposalAwardedUseCase
    ):
        self.proposal_repo = proposal_repo
        self.platform_port = platform_port
        self.award_use_case = award_use_case
    
    def execute(self, platform: str = 'all'):
        """
        Monitorea propuestas y detecta cambios de estado.
        
        Args:
            platform: 'freelancer', 'upwork', o 'all'
        """
        try:
            # Obtener propuestas activas
            # proposals = self.proposal_repo.get_by_status(['submitted', 'pending_award'])
            # TODO: Implementar filtro por plataforma
            
            logger.info(f"Monitoring proposals for platform: {platform}")
            
            # Para cada propuesta, verificar estado
            # for proposal in proposals:
            #     status = self.platform_port.get_proposal_status(proposal.platform_proposal_id)
            #     
            #     if status == 'awarded':
            #         self.award_use_case.execute(proposal.id, proposal.job_offer_id)
            #     elif status == 'rejected':
            #         self.proposal_repo.update_status(proposal.id, 'rejected_by_client')
            
            logger.info("Proposal monitoring completed")
            
        except Exception as e:
            logger.error(f"Error monitoring proposals: {e}")
            raise
