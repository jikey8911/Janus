import logging
from domain.ports import FreelancePlatformPort, AIServicePort, NotificationPort, JobRepository
from domain.entities import JobOffer

class AwardedProjectUseCase:
    """
    Caso de Uso para gestionar proyectos que han sido adjudicados.
    Genera un plan de implementación y lo envía a Telegram para aprobación.
    """
    def __init__(
        self,
        platform_port: FreelancePlatformPort,
        ai_port: AIServicePort,
        notification_port: NotificationPort,
        job_repo: JobRepository
    ):
        self.platform_port = platform_port
        self.ai_port = ai_port
        self.notification_port = notification_port
        self.job_repo = job_repo

    def execute(self, job: JobOffer):
        """
        Procesa un proyecto adjudicado:
        1. Analiza los requerimientos
        2. Genera un plan de implementación según la categoría
        3. Envía el plan a Telegram para aprobación
        """
        logging.info(f"Procesando proyecto adjudicado: {job.title}")
        
        # Paso 1: Analizar requerimientos
        analysis = self.ai_port.analyze_job(job)
        
        # Paso 2: Generar plan de implementación
        implementation_plan = self._generate_implementation_plan(job, analysis)
        
        # Paso 3: Guardar en BD
        job.status = "awarded"
        self.job_repo.save(job)
        
        # Paso 4: Notificar a Telegram
        self.notification_port.notify_implementation_plan(job, implementation_plan)
        
        logging.info(f"Plan de implementación generado para {job.title}")
        return implementation_plan

    def _generate_implementation_plan(self, job: JobOffer, analysis: dict) -> dict:
        """Genera un plan de implementación basado en la categoría del proyecto."""
        category = job.category or "general"
        
        plans = {
            "web_development": self._plan_web_development,
            "mobile_development": self._plan_mobile_development,
            "data_science": self._plan_data_science,
            "content_creation": self._plan_content_creation,
            "translation": self._plan_translation,
            "general": self._plan_general
        }
        
        plan_generator = plans.get(category.lower().replace(" ", "_"), self._plan_general)
        return plan_generator(job, analysis)

    def _plan_web_development(self, job: JobOffer, analysis: dict) -> dict:
        return {
            "category": "Web Development",
            "phases": [
                {
                    "phase": 1,
                    "name": "Análisis y Diseño",
                    "duration": "3-5 días",
                    "tasks": [
                        "Recopilar requisitos detallados",
                        "Crear wireframes y mockups",
                        "Definir arquitectura técnica"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Desarrollo Frontend",
                    "duration": "7-10 días",
                    "tasks": [
                        "Implementar interfaz de usuario",
                        "Integrar componentes reutilizables",
                        "Testing de UI/UX"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Desarrollo Backend",
                    "duration": "7-10 días",
                    "tasks": [
                        "Implementar APIs",
                        "Configurar base de datos",
                        "Testing de lógica de negocio"
                    ]
                },
                {
                    "phase": 4,
                    "name": "Integración y Testing",
                    "duration": "3-5 días",
                    "tasks": [
                        "Testing de integración",
                        "Testing de seguridad",
                        "Optimización de rendimiento"
                    ]
                },
                {
                    "phase": 5,
                    "name": "Despliegue y Soporte",
                    "duration": "2-3 días",
                    "tasks": [
                        "Despliegue a producción",
                        "Monitoreo inicial",
                        "Soporte post-lanzamiento"
                    ]
                }
            ],
            "estimated_duration": "22-33 días",
            "deliverables": ["Código fuente", "Documentación técnica", "Manual de usuario"]
        }

    def _plan_mobile_development(self, job: JobOffer, analysis: dict) -> dict:
        return {
            "category": "Mobile Development",
            "phases": [
                {
                    "phase": 1,
                    "name": "Diseño y Prototipado",
                    "duration": "3-5 días",
                    "tasks": ["Crear mockups", "Definir flujos de usuario"]
                },
                {
                    "phase": 2,
                    "name": "Desarrollo",
                    "duration": "10-15 días",
                    "tasks": ["Implementar funcionalidades", "Integrar APIs"]
                },
                {
                    "phase": 3,
                    "name": "Testing y QA",
                    "duration": "3-5 días",
                    "tasks": ["Testing en dispositivos", "Corrección de bugs"]
                }
            ],
            "estimated_duration": "16-25 días"
        }

    def _plan_data_science(self, job: JobOffer, analysis: dict) -> dict:
        return {
            "category": "Data Science",
            "phases": [
                {
                    "phase": 1,
                    "name": "Exploración de Datos",
                    "duration": "2-3 días",
                    "tasks": ["Recopilar datos", "Análisis exploratorio"]
                },
                {
                    "phase": 2,
                    "name": "Modelado",
                    "duration": "5-7 días",
                    "tasks": ["Preparar datos", "Entrenar modelos"]
                },
                {
                    "phase": 3,
                    "name": "Evaluación y Entrega",
                    "duration": "2-3 días",
                    "tasks": ["Validar resultados", "Documentación"]
                }
            ],
            "estimated_duration": "9-13 días"
        }

    def _plan_content_creation(self, job: JobOffer, analysis: dict) -> dict:
        return {
            "category": "Content Creation",
            "phases": [
                {
                    "phase": 1,
                    "name": "Investigación y Planificación",
                    "duration": "1-2 días",
                    "tasks": ["Investigar tema", "Definir estructura"]
                },
                {
                    "phase": 2,
                    "name": "Creación de Contenido",
                    "duration": "3-5 días",
                    "tasks": ["Escribir/Crear contenido", "Edición"]
                },
                {
                    "phase": 3,
                    "name": "Revisión y Entrega",
                    "duration": "1-2 días",
                    "tasks": ["Revisión final", "Entrega"]
                }
            ],
            "estimated_duration": "5-9 días"
        }

    def _plan_translation(self, job: JobOffer, analysis: dict) -> dict:
        return {
            "category": "Translation",
            "phases": [
                {
                    "phase": 1,
                    "name": "Traducción",
                    "duration": "Depende del volumen",
                    "tasks": ["Traducir contenido", "Revisión"]
                }
            ],
            "estimated_duration": "Variable según volumen"
        }

    def _plan_general(self, job: JobOffer, analysis: dict) -> dict:
        return {
            "category": "General",
            "phases": [
                {
                    "phase": 1,
                    "name": "Análisis",
                    "duration": "2-3 días",
                    "tasks": ["Entender requisitos"]
                },
                {
                    "phase": 2,
                    "name": "Ejecución",
                    "duration": "5-10 días",
                    "tasks": ["Implementar solución"]
                },
                {
                    "phase": 3,
                    "name": "Entrega",
                    "duration": "1-2 días",
                    "tasks": ["Revisión final", "Entrega"]
                }
            ],
            "estimated_duration": "8-15 días"
        }
