import os
import logging
from typing import List
from domain.ports import FreelancePlatformPort
from domain.entities import JobOffer

class UpworkAdapter(FreelancePlatformPort):
    def __init__(self):
        self.consumer_key = os.getenv("UPWORK_CONSUMER_KEY")
        self.client = "MockClient"

    def search_jobs(self, query: str) -> List[JobOffer]:
        logging.info(f"Searching Upwork for: {query}")
        return []

    def submit_proposal(self, job_id: str, content: str) -> bool:
        logging.info(f"Submitting proposal for job {job_id}...")
        return True
