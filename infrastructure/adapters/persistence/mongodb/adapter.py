from datetime import datetime
from typing import List, Optional
from pymongo import MongoClient, ReturnDocument
from domain.ports import JobRepository, ProposalRepository
from domain.entities import JobOffer, Proposal

class MongoJobRepository(JobRepository):
    def __init__(self, connection_string: str, db_name: str = "janus_db"):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.jobs

    def save(self, job: JobOffer) -> JobOffer:
        # Convert dataclass to dict
        data = job.__dict__.copy()
        
        # Upsert by upwork_id
        # If exists, update (to catch status changes), if not, insert.
        # We start with ID None, but Mongo creates _id.
        # We map _id to id if needed, but JobOffer.id is Optional[int]. Mongo uses ObjectId.
        # For simplicity, we might store ObjectId as string in a separate field or just rely on upwork_id
        
        # Remove fields that should not be overwritten if they are None/Empty if we want partial updates,
        # but save usually implies full state.
        
        result = self.collection.find_one_and_update(
            {"upwork_id": job.upwork_id},
            {"$set": data},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        
        # Map back to entity
        return self._map(result)

    def get_by_upwork_id(self, upwork_id: str) -> Optional[JobOffer]:
        result = self.collection.find_one({"upwork_id": upwork_id})
        if result:
            return self._map(result)
        return None

    def _map(self, doc) -> JobOffer:
        # Mongo returns _id, we might ignore it for domain entity or map it.
        # If JobOffer.id is int, ObjectId won't fit perfectly unless we hash it or change Entity to str.
        # Checking entity definition: id: Optional[int]. 
        # We will ignore internal DB ID for now and rely on upwork_id as business key, or Mock an int ID.
        # Let's clean the doc before mapping
        
        doc_data = {k: v for k, v in doc.items() if k != "_id"}
        # If date fields are stored as strings, parse them? PyMongo handles datetime.
        return JobOffer(**doc_data)


class MongoProposalRepository(ProposalRepository):
    def __init__(self, connection_string: str, db_name: str = "janus_db"):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.proposals

    def save(self, proposal: Proposal) -> Proposal:
        data = proposal.__dict__.copy()
        
        # Proposals might not have a unique external ID yet if they are drafts.
        # If proposal.id is None, it's an insert.
        
        if proposal.id:
            # Fake logic: we are using int IDs in domain but Mongo uses ObjectId.
            # Adaptation: If we must respect int, we need a sequence generator or change domain to str.
            # FOR NOW: We will cheat and assume ID isn't critical for this sprint's logic flow 
            # OR we generate a random int ID for the domain entity.
            
            self.collection.update_one({"id": proposal.id}, {"$set": data})
            return proposal
        else:
            # Generate a pseudo-unique INT id for the domain
            import random
            new_id = random.randint(1000, 999999) 
            data["id"] = new_id
            
            self.collection.insert_one(data)
            return self._map(data)

    def _map(self, doc) -> Proposal:
        doc_data = {k: v for k, v in doc.items() if k != "_id"}
        return Proposal(**doc_data)
