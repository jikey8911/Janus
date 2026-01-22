# Plan de Implementación: Project Janus (V2.1 - Arquitectura Hexagonal)

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

### Sprint 4: Mensajería e Inbound (Arquitectura Híbrida)
**Objetivo:** Que Janus "escuche" y reaccione a eventos externos de forma eficiente.
* **HU 4.1: Puerto de Entrada (Inbound Listener):**
    * Implementar Estrategia Push (Webhook) para Freelancer.com.
    * Implementar Estrategia Pull (Polling) para Upwork usando Celery Beat (Intervalo 60s).
    * Gestión de checkpoints en MongoDB para evitar duplicidad.
* **HU 4.2: Relay de Mensajería:**
    * Traducir eventos a DomainEvents.
    * Notificaciones en Telegram con contexto del cliente y del Job.
* **HU 4.3: Comandos de Respuesta (Bidireccional):**
    * Comando `/reply [texto]` para responder a la plataforma desde Telegram.
    * Comando `/approve` para autorizar el envío de propuestas en borrador.

### 🔬 Sprint 5: Ejecución (Protocolo Científico)
**Objetivo:** Automatizar la investigación y planificación usando herramientas especializadas.
* **HU 5.1: Caso de Uso "Diagnóstico" (Investigación):**
    * Integración con la API de **Gemini Flash** para investigación de mercado y técnica.
    * Generación de reporte de hallazgos en Markdown.
* **HU 5.2: Caso de Uso "Blueprint" (Planificación):**
    * Generación de plan técnico detallado usando GPT-4o.
    * Definición de arquitectura, tareas y prompts de ejecución.
* **HU 5.3: Orquestador de Herramientas (Router):**
    * Lógica de clasificación para asignar la tarea al Worker externo adecuado (Diseño/Video/Código).

### 🎬 Sprint 6: Producción Multimedia (Workers Externos)
**Objetivo:** Generar entregables usando APIs de terceros.
* **HU 6.1: Worker de Imagen (Microsoft Designer/DALL-E):**
    * Integración con API para generación de assets visuales y diseño gráfico.
* **HU 6.2: Worker de Video (Pictory/CapCut/ElevenLabs):**
    * Flujo de trabajo: Guion (GPT) -> Voz (ElevenLabs) -> Montaje de video (Pictory).
* **HU 6.3: Caso de Uso "Cierre" (Entrega):**
    * Recopilación de entregables de los distintos Workers.
    * Generación de mensaje profesional y entrega en la plataforma externa.

---

## 🛠️ Notas de Implementación (Herramientas Originales)
* **Investigación:** Perplexity AI.
* **Razonamiento/Plan:** GPT-4o.
* **Imágenes:** Microsoft Designer API / DALL-E 3.
* **Video/Audio:** Pictory AI & ElevenLabs.
* **Backend:** FastAPI + Celery + MongoDB.
