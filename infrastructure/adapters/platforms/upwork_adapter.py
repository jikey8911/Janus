import os
from typing import List, Dict, Any
from domain.ports.freelance_platform_port import FreelancePlatformPort
import upwork

class UpworkAdapter(FreelancePlatformPort):
    """
    Adaptador para la plataforma Upwork.
    """

    def __init__(self):
        self.config = {
            "consumer_key": os.getenv("UPWORK_CONSUMER_KEY"),
            "consumer_secret": os.getenv("UPWORK_CONSUMER_SECRET"),
            "access_token": os.getenv("UPWORK_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("UPWORK_ACCESS_TOKEN_SECRET")
        }
        # Solo inicializar si las claves están presentes, para evitar errores en sandbox
        if all(self.config.values()):
            self.client = upwork.Client(self.config)
        else:
            self.client = None

    async def search_projects(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Busca trabajos en Upwork.
        """
        if not self.client:
            # Fallback para pruebas sin credenciales
            return [{"id": "up_1", "title": "Upwork Python Dev", "platform": "upwork"}]

        params = {
            'q': query,
            'sort': 'create_time desc',
            'job_status': 'open'
        }
        params.update(kwargs)
        
        # Nota: La API de Upwork es síncrona, en una implementación real 
        # se debería envolver en un thread pool si es necesario.
        results = self.client.provider_v2.search_jobs(params)
        jobs = results.get('jobs', [])
        
        # Mapear al formato común
        return [
            {
                "id": job.get("id"),
                "title": job.get("title"),
                "description": job.get("snippet"),
                "platform": "upwork",
                "raw_data": job
            }
            for job in jobs
        ]

    async def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """
        Obtiene detalles de un trabajo en Upwork.
        """
        if not self.client:
            return {"id": project_id, "title": "Detalle simulado Upwork"}
            
        job = self.client.provider_v2.get_job_details(project_id)
        return {
            "id": project_id,
            "title": job.get("title"),
            "description": job.get("description"),
            "platform": "upwork",
            "raw_data": job
        }
