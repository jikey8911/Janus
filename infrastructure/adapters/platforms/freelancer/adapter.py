import requests
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Optional
from domain.ports import FreelancePlatformPort
from domain.entities import JobOffer

class FreelancerAdapter(FreelancePlatformPort):
    def __init__(self):
        self.base_url = "https://www.freelancer.com/api"
        self.oauth_token = os.getenv("FREELANCER_OAUTH_TOKEN")
        self.user_id = os.getenv("FREELANCER_USER_ID")
        
        # Configuración de Sesión con Reintentos automáticos
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.oauth_token}",
            "Content-Type": "application/json"
        })
        
        if self.oauth_token and not self.user_id:
            self._auto_fetch_user_id()

    def _auto_fetch_user_id(self):
        try:
            # Usamos self.session en lugar de requests directamente
            response = self.session.get(f"{self.base_url}/users/0.1/self")
            if response.ok:
                self.user_id = str(response.json()['result']['id'])
                logging.info(f"Freelancer: User ID {self.user_id} detectado.")
        except Exception as e:
            logging.error(f"Error crítico en auto-detección: {e}")

    def search_jobs(self, query: str) -> List[JobOffer]:
        url = f"{self.base_url}/projects/0.1/projects/active/"
        params = {
            "query": query,
            "job_details": "true",
            "project_types[]": "fixed",
            "limit": 10,
            "sort_field": "time_submitted",
            "reverse_sort": "true"
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            projects = response.json().get("result", {}).get("projects", [])
            
            # List comprehension para mayor eficiencia en Python
            return [
                JobOffer(
                    upwork_id=str(p.get("id")), 
                    title=p.get("title"),
                    description=p.get("preview_description") or p.get("description", ""),
                    budget=f"{p.get('budget', {}).get('minimum')}-{p.get('budget', {}).get('maximum')} {p.get('currency', {}).get('code')}",
                    min_amount=float(p.get("budget", {}).get("minimum") or 0),
                    currency=p.get("currency", {}).get("code", "USD"),
                    status="pending"
                ) for p in projects
            ]
        except Exception as e:
            logging.error(f"Error en búsqueda: {e}")
            return []

    def submit_proposal(self, job_id: str, content: str, amount: Optional[float] = None) -> bool:
        if not self.user_id:
            return False

        url = f"{self.base_url}/projects/0.1/bids/"
        payload = {
            "project_id": int(job_id),
            "bidder_id": int(self.user_id),
            "amount": amount or 100.0,
            "period": 7,
            "description": content
        }
        
        try:
            response = self.session.post(url, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            logging.error(f"Error al enviar propuesta {job_id}: {e}")
            return False