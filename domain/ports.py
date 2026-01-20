from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import JobOffer, Proposal, ClientMessage

class JobRepository(ABC):
    @abstractmethod
    def save(self, job: JobOffer) -> JobOffer:
        pass

    @abstractmethod
    def get_by_upwork_id(self, upwork_id: str) -> Optional[JobOffer]:
        pass

class ProposalRepository(ABC):
    @abstractmethod
    def save(self, proposal: Proposal) -> Proposal:
        pass

class UpworkPort(ABC):
    @abstractmethod
    def search_jobs(self, query: str) -> List[JobOffer]:
        pass

    @abstractmethod
    def submit_proposal(self, job_id: str, content: str) -> bool:
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
    def notify_message(self, message: ClientMessage) -> bool:
        pass
