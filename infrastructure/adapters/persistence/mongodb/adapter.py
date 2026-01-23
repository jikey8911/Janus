from pymongo import MongoClient, ReturnDocument
from typing import Optional
from domain.ports import JobRepository, ProposalRepository, EventCheckpointRepository
from domain.entities import JobOffer, Proposal
import os
from datetime import datetime

class MongoJobRepository(JobRepository):
    def __init__(self, connection_string: str = None, db_name: str = "janus_db"):
        if connection_string is None:
            connection_string = os.getenv("DATABASE_URL", "mongodb://localhost:27017/")
        
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.jobs

    def save(self, job: JobOffer) -> JobOffer:
        data = job.__dict__.copy()
        self.collection.find_one_and_update(
            {"external_id": job.external_id},
            {"$set": data},
            upsert=True
        )
        return job

    def get_by_external_id(self, external_id: str) -> Optional[JobOffer]:
        doc = self.collection.find_one({"external_id": external_id})
        if doc:
            data = {k: v for k, v in doc.items() if k != "_id"}
            return JobOffer(**data)
        return None

    def get_by_min_score(self, min_score: int, limit: int = 10) -> list[JobOffer]:
        """Obtiene trabajos con un score mínimo en su análisis."""
        cursor = self.collection.find({"analysis.score": {"$gte": min_score}}).sort("analysis.score", -1).limit(limit)
        jobs = []
        for doc in cursor:
            data = {k: v for k, v in doc.items() if k != "_id"}
            jobs.append(JobOffer(**data))
        return jobs

class MongoProposalRepository(ProposalRepository):
    def __init__(self, connection_string: str = None, db_name: str = "janus_db"):
        if connection_string is None:
            connection_string = os.getenv("DATABASE_URL", "mongodb://localhost:27017/")
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.proposals

    def save(self, proposal: Proposal) -> Proposal:
        data = proposal.__dict__.copy()
        if proposal.id:
            self.collection.update_one({"id": proposal.id}, {"$set": data})
        else:
             import random
             data["id"] = random.randint(1000, 999999)
             self.collection.insert_one(data)
             proposal.id = data["id"]
        return proposal

    def get_by_id(self, proposal_id: int) -> Optional[Proposal]:
        doc = self.collection.find_one({"id": proposal_id})
        if doc:
            data = {k: v for k, v in doc.items() if k != "_id"}
            return Proposal(**data)
        return None

    def get_all(self, limit: int = 10) -> list[Proposal]:
        """Obtiene las últimas propuestas."""
        cursor = self.collection.find().sort("_id", -1).limit(limit)
        proposals = []
        for doc in cursor:
            data = {k: v for k, v in doc.items() if k != "_id"}
            proposals.append(Proposal(**data))
        return proposals

class MongoEventCheckpointRepository(EventCheckpointRepository):
    def __init__(self, db_url: str = None, db_name: str = "janus_db"):
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017/")
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db["checkpoints"]

    def get_last_processed_id(self, source: str) -> str:
        doc = self.collection.find_one({"_id": source})
        return doc.get("last_event_id") if doc else ""

    def update_last_processed_id(self, source: str, event_id: str):
        self.collection.update_one(
            {"_id": source},
            {"$set": {"last_event_id": event_id, "updated_at": datetime.utcnow()}},
            upsert=True
        )
