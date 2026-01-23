import logging
from domain.ports import FreelancePlatformPort
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter

class PlatformFactory:
    @staticmethod
    def get_adapter(platform_name: str) -> FreelancePlatformPort:
        platform_name = platform_name.lower()
        if platform_name == "freelancer":
            return FreelancerAdapter()
        elif platform_name == "upwork":
            return UpworkAdapter()
        else:
            logging.warning(f"Plataforma desconocida: {platform_name}. Usando Freelancer por defecto.")
            return FreelancerAdapter()
