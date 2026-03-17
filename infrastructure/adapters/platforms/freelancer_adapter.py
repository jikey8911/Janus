import os
import requests
from typing import List, Dict, Any
from domain.ports.freelance_platform_port import FreelancePlatformPort

class FreelancerAdapter(FreelancePlatformPort):
    """
    Adaptador para la plataforma Freelancer.com utilizando su API oficial.
    """

    def __init__(self):
        self.api_key = os.getenv("FREELANCER_API_KEY")
        self.base_url = "https://www.freelancer.com/api/projects/0.1/projects"

    async def search_projects(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Busca proyectos en Freelancer.com.
        """
        if not self.api_key:
            # Fallback para pruebas sin credenciales
            return [{"id": "fr_1", "title": "Freelancer.com Python Job", "platform": "freelancer"}]

        params = {
            'query': query,
            'job_details': 'true',
            'project_statuses[]': 'active',
            'sort_field': 'time_submitted',
            'reverse_sort': 'true'
        }
        params.update(kwargs)
        
        headers = {
            'freelancer-oauth-v1': self.api_key
        }

        try:
            response = requests.get(f"{self.base_url}/active/", params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            projects = data.get('result', {}).get('projects', [])
            
            # Mapear al formato común
            return [
                {
                    "id": str(project.get("id")),
                    "title": project.get("title"),
                    "description": project.get("preview_description"),
                    "platform": "freelancer",
                    "raw_data": project
                }
                for project in projects
            ]
        except Exception as e:
            print(f"Error buscando proyectos en Freelancer: {e}")
            return []

    async def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """
        Obtiene detalles de un proyecto en Freelancer.com.
        """
        if not self.api_key:
            return {"id": project_id, "title": "Detalle simulado Freelancer"}
            
        headers = {
            'freelancer-oauth-v1': self.api_key
        }

        try:
            response = requests.get(f"{self.base_url}/{project_id}/", headers=headers)
            response.raise_for_status()
            project = response.json().get('result', {})
            
            return {
                "id": str(project.get("id")),
                "title": project.get("title"),
                "description": project.get("description"),
                "platform": "freelancer",
                "raw_data": project
            }
        except Exception as e:
            print(f"Error obteniendo detalles del proyecto {project_id} en Freelancer: {e}")
            return {}
