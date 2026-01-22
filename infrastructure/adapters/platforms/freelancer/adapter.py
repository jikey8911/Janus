import requests
import os
import logging
from typing import List
from domain.ports import FreelancePlatformPort
from domain.entities import JobOffer

class FreelancerAdapter(FreelancePlatformPort):
    """
    Adaptador real para Freelancer.com usando su API v0.1.
    """
    def __init__(self):
        self.api_url = "https://www.freelancer.com/api/projects/0.1/projects/active/"
        self.oauth_token = os.getenv("FREELANCER_OAUTH_TOKEN")
        self.user_id = os.getenv("FREELANCER_USER_ID")
        logging.info("FreelancerAdapter inicializado con configuración de entorno.")

    def search_jobs(self, query: str) -> List[JobOffer]:
        """Busca proyectos activos en Freelancer.com."""
        params = {
            "query": query,
            "job_details": "true",
            "project_types[]": "fixed",
            "limit": 10,
            "sort_field": "time_submitted",
            "reverse_sort": "true"
        }
        headers = {"freelancer-oauth-v1": self.oauth_token} if self.oauth_token else {}
        
        try:
            response = requests.get(self.api_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            projects = data.get("result", {}).get("projects", [])
            job_offers = []
            
            for p in projects:
                budget_min = p.get("budget", {}).get("minimum", 0)
                budget_max = p.get("budget", {}).get("maximum", 0)
                currency = p.get("currency", {}).get("code", "USD")
                
                job_offers.append(JobOffer(
                    upwork_id=str(p.get("id")),
                    title=p.get("title"),
                    description=p.get("preview_description") or p.get("description", ""),
                    budget=f"{budget_min}-{budget_max} {currency}",
                    status="pending"
                ))
            logging.info(f"Se encontraron {len(job_offers)} proyectos nuevos en Freelancer.")
            return job_offers
        except Exception as e:
            logging.error(f"Error en polling de Freelancer: {e}")
            return []

    def submit_proposal(self, job_id: str, content: str) -> bool:
        """Envía una propuesta (bid) a un proyecto específico."""
        if not self.oauth_token or not self.user_id:
            logging.error("Faltan credenciales para enviar propuesta a Freelancer.")
            return False

        url = "https://www.freelancer.com/api/projects/0.1/bids/"
        payload = {
            "project_id": int(job_id),
            "bidder_id": int(self.user_id),
            "amount": 100, # Valor por defecto, debería ser dinámico
            "period": 7,   # Días por defecto
            "description": content
        }
        headers = {"freelancer-oauth-v1": self.oauth_token}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                logging.info(f"Propuesta enviada con éxito al proyecto {job_id}")
                return True
            else:
                logging.error(f"Error al enviar propuesta: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Excepción al enviar propuesta a Freelancer: {e}")
            return False
