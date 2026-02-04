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

    def get_my_skill_ids(self) -> List[int]:
        """Obtiene la lista de IDs de habilidades del perfil autenticado."""
        try:
            # El ID '0.1/self' devuelve tu propia información
            url = f"{self.base_url}/users/0.1/self/"
            params = {"jobs": "true"} # Solicitamos que incluya los jobs (skills)
            
            response = self.session.get(url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                # Extraemos solo los IDs de la lista de 'jobs'
                skills = data.get('result', {}).get('jobs', [])
                skill_ids = [s.get('id') for s in skills]
                logging.info(f"Habilidades detectadas en tu perfil: {len(skill_ids)}")
                return skill_ids
            else:
                logging.error(f"Error obteniendo habilidades: {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"Error en get_my_skill_ids: {e}")
            return []

    def get_my_skill_names(self) -> List[str]:
        """Obtiene la lista de NOMBRES de habilidades del perfil autenticado."""
        try:
            url = f"{self.base_url}/users/0.1/self/"
            params = {"jobs": "true"}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                skills = data.get('result', {}).get('jobs', [])
                # Extraer nombres
                skill_names = [s.get('name') for s in skills if s.get('name')]
                logging.info(f"Nombres de habilidades detectadas: {skill_names[:5]}... (Total: {len(skill_names)})")
                return skill_names
            else:
                return []
        except Exception as e:
            logging.error(f"Error en get_my_skill_names: {e}")
            return []

    def search_jobs(self, query: str = "", limit: int = 30) -> List[JobOffer]:
        """
        Busca trabajos en Freelancer.com
        Si query está vacío, retorna los últimos trabajos (por defecto 10).
        """
        # 1. Obtener tus habilidades actuales
        my_skills = self.get_my_skill_ids()

        url = f"{self.base_url}/projects/0.1/projects/active/"
        
        # Parámetros base
        params = {
            "job_details": "true",
            # "project_types[]": "fixed", # Eliminado para permitir hourly también
            "limit": limit,
            "sort_field": "time_submitted",
            "compact": "true",
            "full_description": "true",
            # "project_upgrades[]": [], # Eliminado featured y urgent
            # "min_avg_price": 10,  # Eliminado para admitir todos los presupuestos/monedas
            # "max_avg_price": 24000 # Eliminado para admitir todos
        }
        
        # Añadir query solo si se proporciona
        if query:
            params["query"] = query
        
        try:
            logging.info(f"Buscando trabajos en Freelancer (query: '{query or 'últimos 30'}')")
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
                # --- FILTROS DESACTIVADOS PARA OBTENER TODO EL FEED ---
                
                # 1. Filtro de Habilidades (DESACTIVADO)
                # if p.get('is_skill_required') is True: ...

                # 2. Filtro de Presupuesto (DESACTIVADO)
                # budget_data = p.get('budget', {}) ...

                # 3. Filtro Premium (DESACTIVADO)
                # if p.get('is_premium_only') is True: ...

                # 4. Filtro Featured/Sealed (DESACTIVADO)
                # upgrades = p.get('upgrades', {}) ...  
                
                # 5. Filtro Reputación (DESACTIVADO)
                # bid_stats = p.get('bid_stats', {}) ...

                # 6. Filtro Cualificaciones (DESACTIVADO)
                # qualifications = p.get('qualifications', []) ...


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
        """Envía una propuesta a un trabajo validando restricciones de cuenta básica."""
        if not self.user_id:
            logging.error("No se puede enviar propuesta: user_id no disponible")
            return False

        # --- VALIDACIÓN DE SEGURIDAD PARA CUENTA NO-PREMIUM ---
        # Si el monto es >= 2500, Freelancer requiere verificación de identidad (Error 403)
        current_amount = amount or 100.0
        if current_amount >= 2500:
            logging.warning(f"⚠️ Bloqueo preventivo: No se puede ofertar ${current_amount} sin cuenta verificada.")
            return False

        url = f"{self.base_url}/projects/0.1/bids/"
        try:
            payload = {
                "project_id": int(job_id),
                "bidder_id": int(self.user_id),
                "amount": current_amount,
                "period": 7,
                "milestone_percentage": 100,
                "description": content
            }
        except ValueError as e:
            logging.error(f"Error de conversión de tipos para envío (ID debe ser int): {e}")
            return False
        
        try:
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code in [200, 201]:
                logging.info(f"✅ Propuesta enviada exitosamente a job {job_id}")
                return True
            
            # Manejo específico de errores conocidos para depuración
            error_data = response.json() if response.status_code == 403 else {}
            error_code = error_data.get("error_code", "")

            if "RESTRICTED_FROM_BIDDING" in error_code:
                logging.error(f"❌ Bloqueo por restricciones de Freelancer (Membresía/Estrellas): {error_code}")
            else:
                logging.error(f"Error enviando propuesta: {response.status_code} - {response.text}")
            
            return False
                
        except Exception as e:
            logging.error(f"Error crítico al enviar propuesta {job_id}: {e}")
            return False

    # ========== PlatformEventPort Implementation ==========
    
    def get_platform_notifications(self) -> List[dict]:
        """
        Obtiene notificaciones generales y de proyectos de Freelancer.com.
        """
        all_events = []
        
        # 1. Notificaciones generales
        notifs = self.fetch_notifications()
        if notifs and 'notifications' in notifs:
            for n in notifs['notifications']:
                n['source'] = 'general_notifications'
                all_events.append(n)
        
        # 2. Actualizaciones de proyectos (adjudicaciones)
        projects = self.fetch_project_updates()
        if projects and 'projects' in projects:
            for p in projects['projects']:
                p['source'] = 'project_updates'
                all_events.append(p)
                
        return all_events

    def fetch_notifications(self, limit: int = 5) -> Optional[dict]:
        """Consulta la API de notificaciones de Freelancer."""
        url = f"{self.base_url}/notifications/0.1/notifications/"
        params = {"limit": limit}
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.ok:
                return response.json().get('result', {})
            logging.error(f"Error fetching notifications: {response.status_code}")
            return None
        except Exception as e:
            logging.error(f"Network error fetching notifications: {e}")
            return None

    def fetch_project_updates(self, limit: int = 10) -> Optional[dict]:
        """Consulta la API de proyectos (donde somos freelancer o dueños)."""
        url = f"{self.base_url}/projects/0.1/projects/"
        params = {
            "role": "freelancer",
            "status": "active",
            "limit": limit
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.ok:
                return response.json().get('result', {})
            logging.error(f"Error fetching project updates: {response.status_code}")
            return None
        except Exception as e:
            logging.error(f"Network error fetching project updates: {e}")
            return None

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