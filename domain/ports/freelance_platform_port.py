from abc import ABC, abstractmethod
from typing import List, Dict, Any

class FreelancePlatformPort(ABC):
    """
    Define la interfaz (puerto) para interactuar con cualquier plataforma freelance.
    """

    @abstractmethod
    async def search_projects(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Busca proyectos en la plataforma freelance.
        :param query: Término de búsqueda.
        :param kwargs: Parámetros adicionales específicos de la plataforma.
        :return: Una lista de diccionarios, cada uno representando un proyecto.
        """
        pass

    @abstractmethod
    async def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """
        Obtiene los detalles de un proyecto específico.
        :param project_id: ID del proyecto en la plataforma.
        :return: Un diccionario con los detalles del proyecto.
        """
        pass

    # Se pueden añadir más métodos abstractos según sea necesario, por ejemplo:
    # @abstractmethod
    # async def submit_proposal(self, project_id: str, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Envía una propuesta para un proyecto.
    #     """
    #     pass
