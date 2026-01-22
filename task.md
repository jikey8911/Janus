Seguimiento de Tareas: Project Janus (Status Update)
[X] Sprint 1: Capa de Dominio y Puertos
 HU 1.1: Definir Entidades de Dominio (JobOffer, Proposal, ClientMessage)
 HU 1.2: Definir Puertos de Salida - Repositorios (JobRepository, ProposalRepository)
 HU 1.3: Definir Puertos de Salida - Servicios (FreelancePlatformPort, AIServicePort, NotificationPort)
 HU 1.4: Refactorizar Estructura (domain/, application/, infrastructure/)
[X] Sprint 2: Capa de Aplicación (Casos de Uso)
 HU 2.1: Caso de Uso "Buscar y Analizar Ofertas" (ScanAndAnalyzeJobsUseCase)
 HU 2.2: Caso de Uso "Generar Propuesta" (Integrado con OpenAI y Celery)
 HU 2.3: Caso de Uso "Notificar Oportunidad" (Optimizado con acciones rápidas de Telegram)
 HU 2.4: Integrar Casos de Uso con Celery (Soporte Freelancer/Upwork)
[X] Sprint 3: Capa de Infraestructura (Adaptadores)
 HU 3.1: Adaptadores de Persistencia (PostgreSQL/MongoDB)
 HU 3.2: Adaptadores de Plataforma:
 Adaptador Upwork
 Adaptador Freelancer (PRIORITARIO)
 HU 3.3: Adaptadores de Análisis (OpenAI/Gemini)
 HU 3.4: Adaptador de Notificación (Telegram)
 HU 3.5: Adaptador de Ejecución (Estructura de Workers para IA Multimedia)
[X] Sprint 4: Mensajería e Inbound (Arquitectura Híbrida)
 HU 4.1: Puerto de Entrada (Inbound Listener):
 Estrategia Push (Webhook) para Freelancer.com
 Estrategia Pull (Polling) para Upwork (Celery Beat 60s)
 Gestión de checkpoints en MongoDB
 HU 4.2: Relay de Mensajería:
 Traducir eventos a DomainEvents
 Notificaciones en Telegram con contexto
 HU 4.3: Comandos de Respuesta (Bidireccional):
 Comando /reply [texto]
 Comando /approve
[/] Sprint 5: Ejecución (Protocolo Científico)
HU 5.1: Caso de Uso "Diagnóstico" (Investigación):
 Integración API Gemini Flash (Investigación Rápida)
 Reporte de hallazgos en Markdown
 HU 5.2: Caso de Uso "Blueprint" (Planificación):
 Generación de plan técnico con GPT-4o
 HU 5.3: Orquestador de Herramientas (Router):
 Lógica de clasificación (Diseño/Video/Código)
[ ] Sprint 6: Producción Multimedia (Workers Externos)
 HU 6.1: Worker de Imagen (Microsoft Designer/DALL-E)
 HU 6.2: Worker de Video (Pictory/CapCut/ElevenLabs):
 Guion -> Voz -> Montaje
 HU 6.3: Caso de Uso "Cierre" (Entrega):
 Recopilación y entrega en plataforma