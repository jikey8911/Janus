from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class JobOffer:
    """Entidad de Dominio para una Oferta de Trabajo de Upwork."""
    upwork_id: str
    title: str
    description: str
    budget: str
    id: Optional[int] = None # ID interno de la DB
    category: Optional[str] = None
    status: str = "pending" # pending, analyzed, proposed, accepted
    created_at: Optional[datetime] = None

@dataclass(frozen=True)
class Proposal:
    """Entidad de Dominio para una Propuesta generada."""
    job_offer_id: int
    content: str
    id: Optional[int] = None
    status: str = "draft" # draft, sent, accepted
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
