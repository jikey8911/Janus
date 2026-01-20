# Detalle de Sprints Futuros (4 al 6): Janus V2.0

Este documento desglosa técnica y funcionalmente las historias de usuario restantes para completar la visión del **Protocolo Universal de Desarrollo**.

---

## 🚀 Sprint 4: Mensajería e Inbound (El Sistema "Escucha")

**Objetivo:** Transformar Janus de un sistema unidireccional (solo envía notificaciones) a uno bidireccional (recibe mensajes, órdenes y feedback).

### HU 4.1: Puerto de Entrada (Inbound Listener)
*   **Objetivo:** Detectar eventos en las plataformas externas (Upwork/Freelancer) en tiempo casi real.
*   **Lógica de Implementación:**
    *   Crear `FreelancePlatformListenerPort` (Puerto de Entrada).
    *   Implementar Polling (consultar API cada 60s) para detectar:
        *   Nuevos mensajes de chat.
        *   Cambios de estado en propuestas (Accepted/Rejected).
        *   Invitaciones a entrevistas.
    *   Si se detecta un evento, disparar un evento de dominio internamente.

### HU 4.2: Relay de Mensajes a Telegram
*   **Objetivo:** Que el usuario reciba en su Telegram cualquier mensaje escrito por un cliente en Upwork/Freelancer.
*   **Lógica de Implementación:**
    *   Escuchar el evento de dominio `NewClientMessageReceived`.
    *   Buscar el contexto del trabajo (Job ID) asociado.
    *   Formatear el mensaje: `📩 Cliente (Job: Python Bot): "Hola, ¿estás disponible?"`
    *   Usar `NotificationPort` para enviarlo a Telegram.

### HU 4.3: Comandos en Telegram (Webhooks)
*   **Objetivo:** Permitir al usuario responder o dar órdenes desde Telegram.
*   **Lógica de Implementación:**
    *   Exponer un endpoint HTTP (FastAPI) `/webhook/telegram`.
    *   Configurar el Bot de Telegram para enviar updates a este endpoint.
    *   Parsear comandos:
        *   `/reply [mensaje]`: Envía respuesta al cliente del último contexto activo.
        *   `/approve [proposal_id]`: Autoriza el envío de una propuesta borrador.
    *   Invocar los Casos de Uso correspondientes (`ReplyToClientUseCase`, `SubmitProposalUseCase`).

---

## 🔬 Sprint 5: Ejecución (Protocolo Científico)

**Objetivo:** Automatizar la fase de investigación y planificación de los proyectos ganados, aplicando el método científico.

### HU 5.1: Caso de Uso "Diagnóstico" (Investigación)
*   **Objetivo:** Antes de escribir una línea de código, entender el problema profundamente.
*   **Lógica de Implementación:**
    *   Integrar API de **Perplexity** (o herramienta de búsqueda similar).
    *   Dada una descripción de trabajo, generar preguntas de investigación: "¿Qué librerías existen para X?", "¿Competidores de Y?".
    *   Ejecutar búsqueda y compilar un "Resumen de Investigación" en Markdown.

### HU 5.2: Caso de Uso "Blueprint" (Planificación Técnica)
*   **Objetivo:** Generar un plan de arquitectura y pasos a seguir (Implementation Plan).
*   **Lógica de Implementación:**
    *   Usar `AIServicePort` (GPT-4o) con el contexto del trabajo + el "Resumen de Investigación".
    *   Prompt de Sistema: "Eres un Arquitecto de Software. Genera un plan de implementación paso a paso...".
    *   Output: Un archivo `blueprint.md` que el usuario debe aprobar.

### HU 5.3: Orquestador de Herramientas (Categorizador)
*   **Objetivo:** Decidir qué "Worker" especializado ejecutar según la naturaleza de la tarea.
*   **Lógica de Implementación:**
    *   Clasificar la tarea entrante: ¿Es Código? ¿Es Video? ¿Es Diseño Gráfico?
    *   **Router:**
        *   Si es Código -> Asignar al humano (o agente de código futuro).
        *   Si es Video -> Asignar al Worker de Video (Sprint 6).
        *   Si es Imagen -> Asignar al Worker de Imagen (Sprint 6).

---

## 🎬 Sprint 6: Producción y Entrega Multimedia

**Objetivo:** Dotar a Janus de "brazos" creativos para generar entregables multimedia automáticamente.

### HU 6.1: Worker de Imagen (Diseño)
*   **Objetivo:** Generar assets visuales (logos, banners, posts).
*   **Lógica de Implementación:**
    *   Implementar `MultimediaWorkerPort` para imágenes.
    *   Integrar API de **DALL-E 3** o **Microsoft Designer**.
    *   Flujo: Recibir Prompt -> Generar Imagen -> Devolver URL/Archivo -> Enviar al Cliente.

### HU 6.2: Worker de Video (Edición/Generación)
*   **Objetivo:** Crear contenido de video para marketing o tutoriales.
*   **Lógica de Implementación:**
    *   Implementar `MultimediaWorkerPort` para video.
    *   Integrar API de **ElevenLabs** (Audio/Voz) + **Pictory/CapCut** (Video).
    *   Flujo: Guion (GPT) -> Audio (ElevenLabs) -> Video Sync (Pictory) -> Render Final.

### HU 6.3: Caso de Uso "Cierre" (Entrega)
*   **Objetivo:** Empaquetar todo el trabajo y entregarlo formalmente para cobrar.
*   **Lógica de Implementación:**
    *   Recopilar todos los entregables (código, imágenes, videos).
    *   Generar un mensaje de cierre profesional: "Hola, aquí adjunto los entregables finales...".
    *   Invocar `SubmitWorkUseCase` (subir archivos a la plataforma).
    *   Cerrar el ciclo de la tarea con status `Completed`.
