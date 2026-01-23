from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

@dataclass(frozen=False)
class JobOffer:
    """Entidad de Dominio para una Oferta de Trabajo."""
    external_id: str
    title: str
    description: str
    budget: str
    min_amount: float
    currency: str
    status: str = "pending"
    category: Optional[str] = None
    platform: str = "freelancer" # freelancer, upwork
    analysis: Optional[dict] = None # Almacena el resultado de la IA
    id: Optional[int] = None

@dataclass(frozen=False)
class Proposal:
    """Entidad de Dominio para una Propuesta generada."""
    job_offer_id: Union[int, str]
    content: str
    id: Optional[int] = None
    bid_amount: Optional[float] = None
    currency: Optional[str] = None
    # Estados: draft, approved, submitted, pending_award, awarded, rejected_by_client, withdrawn, expired
    status: str = "draft"
    platform_proposal_id: Optional[str] = None
    platform: str = "freelancer" # freelancer, upwork
    submitted_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    awarded_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

@dataclass(frozen=True)
class ClientMessage:
    """Entidad de Dominio para un mensaje de un cliente en Upwork."""
    client_name: str
    message_content: str
    job_context: str
    id: Optional[int] = None
    suggested_reply: Optional[str] = None
    created_at: Optional[datetime] = None
