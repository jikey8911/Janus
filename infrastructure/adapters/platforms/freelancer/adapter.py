import requests
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Optional
from datetime import datetime
from domain.ports import FreelancePlatformPort, PlatformEventPort
from domain.entities import JobOffer, ClientMessage

class FreelancerAdapter(FreelancePlatformPort, PlatformEventPort):
    """
    Adaptador para Freelancer.com
    Estrategia de notificaciones: Webhooks (Push)
    """
    def __init__(self):
        self.base_url = "https://www.freelancer.com/api"
        self.client_id = os.getenv("FREELANCER_CLIENT_ID")
        self.client_secret = os.getenv("FREELANCER_CLIENT_SECRET")
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
        
        # Inicializar headers (se actualizarán en _authenticate)
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        # Autenticación automática
        self._authenticate()

    def _authenticate(self):
        """
        Maneja la autenticación automática.
        Si el token es inválido o 'pending_auth_flow', intenta obtener uno nuevo.
        """
        try:
            # Si el token es el placeholder o no existe, intentar obtener uno nuevo
            if not self.oauth_token or self.oauth_token == "pending_auth_flow":
                if self.client_id and self.client_secret:
                    logging.info("Freelancer: Intentando autenticación automática (client_credentials)...")
                    token_url = "https://accounts.freelancer.com/oauth/token"
                    payload = {
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "basic"
                    }
                    response = requests.post(token_url, data=payload, timeout=10)
                    if response.ok:
                        self.oauth_token = response.json().get("access_token")
                        logging.info("Freelancer: Access Token obtenido exitosamente.")
                    else:
                        logging.error(f"Freelancer: Falló autenticación automática: {response.status_code}")
                else:
                    logging.warning("Freelancer: No hay token ni credenciales para autenticación automática.")

            # Configurar Authorization header
            if self.oauth_token and self.oauth_token != "pending_auth_flow":
                self.session.headers.update({"Authorization": f"Bearer {self.oauth_token}"})
                
                # Intentar obtener User ID si no lo tenemos
                if not self.user_id:
                    self._auto_fetch_user_id()
            
        except Exception as e:
            logging.error(f"Error en proceso de autenticación: {e}")

    def _auto_fetch_user_id(self):
        """Obtiene el User ID automáticamente usando el token actual."""
        try:
            response = self.session.get(f"{self.base_url}/users/0.1/self", timeout=10)
            if response.ok:
                self.user_id = str(response.json()['result']['id'])
                logging.info(f"Freelancer: User ID {self.user_id} detectado.")
            else:
                logging.error(f"Error obteniendo user ID: {response.status_code}")
        except Exception as e:
            logging.error(f"Error crítico en detección de User ID: {e}")

    # ========== FreelancePlatformPort Implementation ==========

    def search_jobs(self, query: str = "", limit: int = 10) -> List[JobOffer]:
        """
        Busca trabajos en Freelancer.com
        Si query está vacío, retorna los últimos trabajos (por defecto 10).
        """
        url = f"{self.base_url}/projects/0.1/projects/active/"
        
        # Parámetros base
        params = {
            "job_details": "true",
            "project_types[]": "fixed",
            "limit": limit,
            "sort_field": "time_submitted",
            "compact": "true"
        }
        
        # Añadir query solo si se proporciona
        if query:
            params["query"] = query
        
        try:
            logging.info(f"Buscando trabajos en Freelancer (query: '{query or 'últimos 10'}')")
            response = self.session.get(url, params=params, timeout=15)
            
            # Log detallado para debugging
            logging.info(f"Response status: {response.status_code}")
            if response.status_code != 200:
                logging.error(f"Error response: {response.text[:500]}")
            
            response.raise_for_status()
            
            data = response.json()
            projects = data.get("result", {}).get("projects", [])
            
            logging.info(f"Encontrados {len(projects)} trabajos")
            
            # Mapear a JobOffer
            jobs = []
            for p in projects:
                try:
                    budget_data = p.get('budget', {})
                    currency_data = p.get('currency', {})
                    
                    min_amount = float(budget_data.get('minimum', 0))
                    max_amount = float(budget_data.get('maximum', 0))
                    currency_code = currency_data.get('code', 'USD')
                    
                    job = JobOffer(
                        external_id=str(p.get("id")),
                        title=p.get("title", "Sin título"),
                        description=p.get("preview_description") or p.get("description", ""),
                        budget=f"{min_amount}-{max_amount} {currency_code}",
                        min_amount=min_amount,
                        currency=currency_code,
                        status="pending"
                    )
                    jobs.append(job)
                except Exception as e:
                    logging.warning(f"Error mapeando proyecto {p.get('id')}: {e}")
                    continue
            
            return jobs
            
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error en búsqueda: {e}")
            logging.error(f"Response: {e.response.text if e.response else 'No response'}")
            return []
        except Exception as e:
            logging.error(f"Error en búsqueda: {e}")
            import traceback
            traceback.print_exc()
            return []

    def submit_proposal(self, job_id: str, content: str, amount: Optional[float] = None) -> bool:
        """Envía una propuesta a un trabajo."""
        if not self.user_id:
            logging.error("No se puede enviar propuesta: user_id no disponible")
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
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code in [200, 201]:
                logging.info(f"Propuesta enviada exitosamente a job {job_id}")
                return True
            else:
                logging.error(f"Error enviando propuesta: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error al enviar propuesta {job_id}: {e}")
            return False

    # ========== PlatformEventPort Implementation ==========
    
    def get_proposal_status(self, proposal_id: str) -> str:
        """
        Consulta el estado de una propuesta.
        Usado como fallback si webhook falla.
        
        Returns:
            'pending', 'awarded', 'rejected', 'expired'
        """
        try:
            url = f"{self.base_url}/projects/0.1/bids/{proposal_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            bid_data = data.get('result', {})
            
            # Mapear estado de Freelancer a estados internos
            status_map = {
                'pending': 'pending',
                'accepted': 'awarded',
                'rejected': 'rejected',
                'expired': 'expired',
                'withdrawn': 'withdrawn',
                'complete': 'awarded'
            }
            
            freelancer_status = bid_data.get('status', 'pending')
            internal_status = status_map.get(freelancer_status, 'pending')
            
            logging.info(f"Proposal {proposal_id} status: {freelancer_status} → {internal_status}")
            return internal_status
            
        except Exception as e:
            logging.error(f"Error getting proposal status: {e}")
            return 'pending'
    
    def get_new_messages(self, proposal_id: str, since: datetime) -> List[ClientMessage]:
        """
        Obtiene mensajes nuevos del cliente.
        Normalmente llegan por webhook, esto es fallback.
        """
        try:
            # TODO: Implementar consulta a API de mensajes de Freelancer
            # Endpoint aproximado: GET /messages/0.1/threads/{thread_id}/messages
            logging.info(f"Checking messages for proposal {proposal_id} since {since}")
            
            # Por ahora retorna lista vacía (webhook es la estrategia principal)
            return []
            
        except Exception as e:
            logging.error(f"Error getting messages: {e}")
            return []
    
    def send_message(self, proposal_id: str, content: str) -> bool:
        """
        Envía un mensaje al cliente.
        """
        try:
            # TODO: Implementar envío de mensaje via API de Freelancer
            # Endpoint aproximado: POST /messages/0.1/threads/{thread_id}/messages
            logging.info(f"Sending message to proposal {proposal_id}: {content[:50]}...")
            
            # Simulación por ahora
            # En producción, necesitaremos:
            # 1. Obtener thread_id del proposal
            # 2. POST al endpoint de mensajes
            
            return True
            
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            return False