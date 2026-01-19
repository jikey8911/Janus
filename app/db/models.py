from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .session import Base

class JobOffer(Base):
    __tablename__ = "job_offers"

    id = Column(Integer, primary_key=True, index=True)
    upwork_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    budget = Column(String)
    category = Column(String)
    status = Column(String, default="pending") # pending, analyzed, proposed, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    job_offer_id = Column(Integer)
    content = Column(Text)
    status = Column(String, default="draft") # draft, sent, accepted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
