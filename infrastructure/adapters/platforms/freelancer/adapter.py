import requests
import os
import logging
from typing import List, Optional
from domain.ports import FreelancePlatformPort
from domain.entities import JobOffer

class FreelancerAdapter(FreelancePlatformPort):
    """
    Adaptador de Freelancer.com con Auto-Configuración.
    Aplica:
    1. Headers OAuth2 estándar.
    2. Mapeo a entidad genérica JobOffer.
    3. Puja dinámica basada en presupuesto del proyecto.
    4. Auto-detección de User ID.
    """
    
    def __init__(self):
        self.base_url = "https://www.freelancer.com/api"
        self.oauth_token = os.getenv("FREELANCER_OAUTH_TOKEN")
        
        # El ID se vuelve opcional; si no está en el .env, el método lo busca.
        self.user_id = os.getenv("FREELANCER_USER_ID")
        
        # Tip 1: Headers centralizados
        self.headers = {
            "Authorization": f"Bearer {self.oauth_token}",
            "Content-Type": "application/json"
        }
        
        if not self.oauth_token:
            logging.error("FreelancerAdapter: No se encontró FREELANCER_OAUTH_TOKEN.")
        
        # Nuevo Método: Auto-obtención del ID al inicializar
        if self.oauth_token and not self.user_id:
            self._auto_fetch_user_id()

    def _auto_fetch_user_id(self):
        """
        NUEVO MÉTODO: Consulta a la API para identificar al usuario dueño del token.
        Esto elimina la necesidad de buscar el ID en el código fuente de la web.
        """
        try:
            url = f"{self.base_url}/users/0.1/self"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                self.user_id = str(response.json()['result']['id'])
                logging.info(f"Freelancer: User ID {self.user_id} detectado exitosamente.")
            else:
                logging.warning("No se pudo detectar el User ID automáticamente.")
        except Exception as e:
            logging.error(f"Error en auto-detección de ID: {e}")

    def search_jobs(self, query: str) -> List[JobOffer]:
        """Busca proyectos activos y mapea a la entidad JobOffer (Tip 2)."""
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
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            projects = data.get("result", {}).get("projects", [])
            job_offers = []
            
            for p in projects:
                # Tip 3: Extraer datos de presupuesto para puja inteligente
                budget = p.get("budget", {})
                b_min = budget.get("minimum") or 0
                b_max = budget.get("maximum") or 0
                currency = p.get("currency", {}).get("code", "USD")
                
                # Mapeo a Entidad Genérica (Tip 2)
                job_offers.append(JobOffer(
                    external_id=str(p.get("id")), 
                    title=p.get("title"),
                    description=p.get("preview_description") or p.get("description", ""),
                    budget=f"{b_min}-{b_max} {currency}",
                    min_amount=float(b_min),
                    currency=currency,
                    status="pending"
                ))
                
            return job_offers
            
        except Exception as e:
            logging.error(f"Freelancer API Search Error: {e}")
            return []

    def submit_proposal(self, job_id: str, content: str, amount: Optional[float] = None) -> bool:
        """
        Envía una propuesta. Si 'amount' es None, usa una puja base.
        """
        if not self.user_id:
            # Reintento de última instancia
            self._auto_fetch_user_id()
            if not self.user_id:
                logging.error("Falta User ID para enviar la propuesta.")
                return False

        url = f"{self.base_url}/projects/0.1/bids/"
        
        # Tip 3: Lógica de puja (monto y duración)
        payload = {
            "project_id": int(job_id),
            "bidder_id": int(self.user_id),
            "amount": amount if amount else 100.0,
            "period": 7,
            "description": content
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201]:
                logging.info(f"Propuesta exitosa para el proyecto {job_id}.")
                return True
            else:
                logging.error(f"Error al ofertar ({response.status_code}): {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Excepción en submit_proposal: {e}")
            return False