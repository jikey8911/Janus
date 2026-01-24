import logging
from domain.ports import FreelancePlatformPort, AIServicePort
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter
from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter
from infrastructure.adapters.analyzer.groq.adapter import GroqAdapter

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

class AIFactory:
    @staticmethod
    def get_adapter(provider_name: str = "groq") -> AIServicePort:
        # Si llega None o vacio, usar default
        if not provider_name:
            provider_name = "groq"
            
        provider_name = provider_name.lower()
        if provider_name == "groq":
            return GroqAdapter()
        elif provider_name == "gemini":
            return GeminiAdapter()
        else:
            logging.warning(f"Proveedor IA desconocido: {provider_name}. Usando Groq por defecto.")
            return GroqAdapter()
