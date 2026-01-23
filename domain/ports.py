from abc import ABC, abstractmethod
from typing import List, Optional, Union
from datetime import datetime
from .entities import JobOffer, Proposal, ClientMessage

class JobRepository(ABC):
    @abstractmethod
    def save(self, job: JobOffer) -> JobOffer:
        pass

    @abstractmethod
    def get_by_external_id(self, external_id: str) -> Optional[JobOffer]:
        pass

class ProposalRepository(ABC):
    @abstractmethod
    def save(self, proposal: Proposal) -> Proposal:
        pass

    @abstractmethod
    def get_by_id(self, proposal_id: int) -> Optional[Proposal]:
        pass

class FreelancePlatformPort(ABC):
    @abstractmethod
    def search_jobs(self, query: str) -> List[JobOffer]:
        pass

    @abstractmethod
    def submit_proposal(self, job_id: str, content: str) -> bool:
        pass

class PlatformEventPort(ABC):
    """
    Puerto para recibir eventos de plataformas freelance.
    Cada adaptador implementa su estrategia (webhook o polling).
    """
    
    @abstractmethod
    def get_proposal_status(self, proposal_id: str) -> str:
        """
        Consulta el estado actual de una propuesta.
        
        Returns:
            'pending', 'awarded', 'rejected', 'expired'
        """
        pass

    @abstractmethod
    def get_platform_notifications(self) -> List[dict]:
        """
        Obtiene notificaciones generales y de proyectos de la plataforma.
        
        Returns:
            Lista de diccionarios con datos crudos de notificaciones.
        """
        pass
    
    @abstractmethod
    def get_new_messages(self, proposal_id: str, since: datetime) -> List[ClientMessage]:
        """
        Obtiene mensajes nuevos del cliente desde un timestamp.
        
        Args:
            proposal_id: ID de la propuesta en la plataforma
            since: Timestamp desde el cual buscar mensajes
            
        Returns:
            Lista de mensajes nuevos
        """
        pass
    
    @abstractmethod
    def send_message(self, proposal_id: str, content: str) -> bool:
        """
        Envía un mensaje al cliente.
        
        Args:
            proposal_id: ID de la propuesta
            content: Contenido del mensaje
            
        Returns:
            True si se envió exitosamente
        """
        pass

class AIServicePort(ABC):
    @abstractmethod
    def analyze_job(self, job: JobOffer) -> dict:
        pass

    @abstractmethod
    def suggest_reply(self, message: ClientMessage) -> str:
        pass

    @abstractmethod
    def generate_proposal_content(self, job: JobOffer) -> str:
        pass

class NotificationPort(ABC):
    @abstractmethod
    def notify_opportunity(self, job: JobOffer, analysis: dict) -> bool:
        pass

    @abstractmethod
    def send_proposal_for_validation(
        self, 
        job_title: str, 
        proposal_content: str, 
        proposal_id: int,
        job_id: str,
        analysis_score: Optional[int] = None,
        bid_amount: Optional[float] = None,
        currency: Optional[str] = "USD"
    ) -> bool:
        pass

    @abstractmethod
    def notify_message(self, message: Union[ClientMessage, str]) -> bool:
        pass

    @abstractmethod
    def notify_error(self, message: str) -> bool:
        pass

    @abstractmethod
    def notify_warning(self, message: str) -> bool:
        pass

class EventCheckpointRepository(ABC):
    @abstractmethod
    def get_last_processed_id(self, source: str) -> str:
        """
        Retrieves the last processed event ID for a given source.
        """
        pass

    @abstractmethod
    def update_last_processed_id(self, source: str, event_id: str):
        """
        Updates the checkpoint for a source.
        """
        pass
