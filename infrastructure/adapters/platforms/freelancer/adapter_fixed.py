import requests
import os
import logging
from typing import List
from domain.ports import FreelancePlatformPort
from domain.entities import JobOffer

class FreelancerAdapterFixed(FreelancePlatformPort):
    """
    Adaptador mejorado para Freelancer.com con manejo robusto de errores.
    """
    def __init__(self):
        self.api_url = "https://www.freelancer.com/api/projects/0.1/projects/active"
        self.oauth_token = os.getenv("FREELANCER_OAUTH_TOKEN")
        self.user_id = os.getenv("FREELANCER_USER_ID")
        self.session = requests.Session()
        if self.oauth_token:
            self.session.headers.update({"freelancer-oauth-v1": self.oauth_token})
        logging.info("FreelancerAdapterFixed inicializado")

    def search_jobs(self, query: str) -> List[JobOffer]:
        """Busca proyectos activos en Freelancer.com con filtros mejorados."""
        params = {
            "query": query,
            "job_details": "true",
            "project_types[]": "fixed",
            "limit": 10,
            "sort_field": "time_submitted",
            "reverse_sort": "true"
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("status") == "success":
                logging.warning(f"Respuesta no exitosa de Freelancer: {data}")
                return []
            
            projects = data.get("result", {}).get("projects", [])
            job_offers = []
            
            for p in projects:
                try:
                    budget_min = p.get("budget", {}).get("minimum", 0)
                    budget_max = p.get("budget", {}).get("maximum", 0)
                    currency = p.get("currency", {}).get("code", "USD")
                    
                    job_offers.append(JobOffer(
                        upwork_id=str(p.get("id")),
                        title=p.get("title", "Sin título"),
                        description=p.get("preview_description") or p.get("description", ""),
                        budget=f"{budget_min}-{budget_max} {currency}",
                        category=p.get("category", {}).get("name"),
                        status="pending"
                    ))
                except Exception as e:
                    logging.error(f"Error procesando proyecto: {e}")
                    continue
            
            logging.info(f"Se encontraron {len(job_offers)} proyectos en Freelancer")
            return job_offers
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en polling de Freelancer: {e}")
            return []

    def submit_proposal(self, job_id: str, content: str, bid_amount: float = 100) -> bool:
        """Envía un bid (propuesta) a un proyecto específico."""
        if not self.oauth_token or not self.user_id:
            logging.error("Faltan credenciales de Freelancer (TOKEN o USER_ID)")
            return False

        url = "https://www.freelancer.com/api/projects/0.1/bids"
        
        payload = {
            "project_id": int(job_id),
            "bidder_id": int(self.user_id),
            "amount": bid_amount,
            "period": 7,
            "description": content
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("status") == "success":
                logging.info(f"Bid enviado exitosamente al proyecto {job_id}")
                return True
            else:
                logging.error(f"Error al enviar bid: {result.get('message', 'Unknown error')}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción al enviar bid: {e}")
            return False
