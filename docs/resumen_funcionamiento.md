# Plan de Implementación: Project Janus (V2.0 - Arquitectura Hexagonal)

## Visión del Proyecto
Refactorizar y expandir "Project Janus" para automatizar no solo la captación, sino también la producción y entrega de servicios freelance mediante el **Protocolo Universal de Desarrollo (Método Científico)** y el uso coordinado de herramientas de IA.

## Épicas (Capas de la Arquitectura Hexagonal)

| Épica | Nombre | Descripción |
| :--- | :--- | :--- |
| **E1** | **Dominio y Puertos** | Núcleo inmutable: Entidades, lógica de negocio y definiciones de interfaces. |
| **E2** | **Aplicación e Interacción** | Casos de uso: Orquestación del Radar, Generación de Propuestas y Protocolos de Ejecución. |
| **E3** | **Infraestructura (Salida)** | Adaptadores: Upwork, Freelancer, Telegram, OpenAI/Gemini, ElevenLabs, Canva. |
| **E4** | **Adaptadores de Entrada** | Escucha activa: Webhooks de Telegram y Monitoreo (Polling) de Upwork/Freelancer. |

---

## Sprints y Tareas Detalladas

### Sprint 1: Capa de Dominio y Puertos (Finalizado/Refinamiento)
* **HU 1.1:** Definir Entidades de Dominio (`JobOffer`, `Proposal`, `ClientMessage`).
* **HU 1.2:** Definir Puertos de Salida de Persistencia (`JobRepository`, `ProposalRepository`).
* **HU 1.3:** Definir Puertos de Salida de Servicios (`FreelancePort`, `AIServicePort`, `NotificationPort`).

### Sprint 2: Casos de Uso de Captación y Notificación
* **HU 2.1:** Caso de Uso `ScanAndAnalyzeJobs`: Orquestación Radar -> IA -> Notificación.
* **HU 2.2:** Caso de Uso `GenerateProposal`: Generar Cover Letter personalizada con IA.
* **HU 2.3:** Integrar con Celery para ejecución en segundo plano cada 30 min.

### Sprint 3: Infraestructura y Adaptadores de Salida
* **HU 3.1:** Adaptadores de DB (PostgreSQL y MongoDB).
* **HU 3.2:** Adaptadores de Plataforma (Upwork y **Freelancer.com**).
* **HU 3.3:** Adaptador de IA (Estandarizar OpenAI/Gemini bajo `AIServicePort`).
* **HU 3.4:** Adaptador de Notificación (Telegram Bot API).

### Sprint 4: Adaptadores de Entrada y Gestión de Mensajes (NUEVO)
* **HU 4.1:** **Inbound Port:** Implementar receptor de mensajes de Upwork/Freelancer (Nuevos mensajes, contratos ganados).
* **HU 4.2:** **Relay de Mensajes:** Si llega un mensaje del cliente, enviarlo a Telegram.
* **HU 4.3:** **Puerto de Entrada Telegram:** Webhook para responder mensajes de clientes desde Telegram.

### Sprint 5: Protocolo Universal de Desarrollo (Ejecución Científica) (NUEVO)
* **HU 5.1:** **Fase I y II (Observación e Hipótesis):** Automatizar investigación con Perplexity AI y generación de Blueprint del proyecto.
* **HU 5.2:** **Categorizador de Trabajo:** Caso de uso que decide qué herramientas usar según el tipo de trabajo (Contenido, Video, Diseño).
* **HU 5.3:** **Fase IV y V (Testing y Feedback):** Implementar flujo de envío de borradores al cliente y captura de feedback.

### Sprint 6: Producción Multimedia y Cierre (NUEVO)
* **HU 6.1:** **Adaptador Multimedia (Texto/Imagen):** Integrar ChatGPT + Canva AI/Microsoft Designer.
* **HU 6.2:** **Adaptador Multimedia (Video/Audio):** Integrar ElevenLabs + CapCut/Pictory.
* **HU 6.3:** **Fase VI (Conclusión):** Generación automática de reportes de entrega y cierre de hito en plataforma.