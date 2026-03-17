import logging
from typing import List, Dict, Any, Optional
from domain.ports.freelance_platform_port import FreelancePlatformPort
from domain.ports import JobRepository, AIServicePort, NotificationPort

class MultiplatformScanAndAnalyzeUseCase:
    """
    Caso de uso para escanear y analizar trabajos de múltiples plataformas freelance.
    """
    def __init__(
        self,
        platforms: List[FreelancePlatformPort],
        job_repo: JobRepository,
        ai_port: AIServicePort,
        notification_port: NotificationPort
    ):
        self.platforms = platforms
        self.job_repo = job_repo
        self.ai_port = ai_port
        self.notification_port = notification_port

    async def execute(self, query: str = "python automation ai", limit_per_platform: int = 10):
        logging.info(f"Iniciando escaneo multiplataforma con query: '{query}'")
        
        all_projects = []
        for platform in self.platforms:
            platform_name = platform.__class__.__name__
            try:
                logging.info(f"Buscando en {platform_name}...")
                projects = await platform.search_projects(query, limit=limit_per_platform)
                logging.info(f"Encontrados {len(projects)} proyectos en {platform_name}")
                all_projects.extend(projects)
            except Exception as e:
                logging.error(f"Error buscando en {platform_name}: {e}")

        for project in all_projects:
            try:
                # Verificar si ya existe en la DB
                external_id = project.get("id")
                platform_name = project.get("platform")
                
                # Nota: El JobRepository actual podría necesitar ajustes para manejar platform + external_id
                # Por ahora simulamos la lógica de análisis
                logging.info(f"Analizando proyecto {external_id} de {platform_name}: {project.get('title')}")
                
                # Aquí iría la lógica de análisis con IA, guardado y notificación
                # similar a ScanAndAnalyzeJobsUseCase.execute()
                
            except Exception as e:
                logging.error(f"Error procesando proyecto {project.get('id')}: {e}")

        return all_projects
