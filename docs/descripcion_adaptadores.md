# Descripción de Adaptadores del Sistema (Capa de Infraestructura)

Este documento describe la funcionalidad actual y esperada de los adaptadores en la Arquitectura Hexagonal de Project Janus.

## 1. Adaptadores de Persistencia (MongoDB)

**Ubicación:** `infrastructure/adapters/persistence/mongodb/adapter.py`
**Estado:** implementado

Encargados de guardar y recuperar el estado de las entidades de dominio en una base de datos MongoDB.

### `MongoJobRepository`
*   **`save(job: JobOffer) -> JobOffer`**
    *   **Qué hace:** Guarda un objeto `JobOffer` en la colección `jobs`. Utiliza `find_one_and_update` con `upsert=True` basado en el campo `upwork_id`. Esto asegura que si la oferta ya existe, se actualice (ej: cambio de estado), y si no, se cree.
    *   **Debería hacer:** Lo implementado es correcto. En el futuro podría mapear el `_id` de Mongo al `id` de la entidad de forma más robusta.
*   **`get_by_upwork_id(upwork_id: str) -> Optional[JobOffer]`**
    *   **Qué hace:** Busca un documento en la colección `jobs` que coincida con el `upwork_id` y lo convierte en una entidad `JobOffer`.

### `MongoProposalRepository`
*   **`save(proposal: Proposal) -> Proposal`**
    *   **Qué hace:** Guarda un objeto `Proposal` en la colección `proposals`.
    *   **Simulación:** Actualmente, si es una nueva propuesta, genera un ID numérico aleatorio (`random.randint`) para simular un auto-incremento y lo inserta. Si ya tiene ID, actualiza el documento existente.
    *   **Debería hacer:** En producción, debería usar UUIDs o manejar la generación de IDs de forma consistente a través de MongoDB.

---

## 2. Adaptadores de Plataforma (Upwork)

**Ubicación:** `infrastructure/adapters/platforms/upwork/adapter.py`
**Estado:** Implementado (Lógica placeholder)

Encargado de la comunicación con la API externa de Upwork.

### `UpworkAdapter`
*   **`__init__`**
    *   **Qué hace:** Carga credenciales de variables de entorno e inicializa el cliente `upwork.Client`. Maneja excepciones si falla la inicialización.
*   **`search_jobs(query: str) -> List[JobOffer]`**
    *   **Qué hace:** Método placeholder. Actualmente retorna una lista vacía `[]` y loguea la acción.
    *   **Debería hacer:** Invocar el endpoint de búsqueda de trabajos de la API de Upwork (ej: `client.search.jobs.find`), mapear los resultados JSON de la API a entidades `JobOffer` y retornarlas.
*   **`submit_proposal(job_id: str, content: str) -> bool`**
    *   **Qué hace:** Método placeholder. Retorna `True` y loguea la acción.
    *   **Debería hacer:** Construir el payload de la propuesta y enviarlo a la API de Upwork para aplicar a la oferta.

---

## 3. Adaptadores de Análisis (IA) - PENDIENTE (HU 3.3)

**Ubicación:** `infrastructure/adapters/analyzer/openai/adapter.py`
**Estado:** Pendiente

Encargado de usar Modelos de Lenguaje (LLMs) para procesar texto y tomar decisiones.

### `OpenAIAdapter` (Futuro)
*   **`analyze_job(job: JobOffer) -> dict`**
    *   **Debería hacer:** Enviar la descripción del trabajo a OpenAI con un prompt de sistema que instruya evaluar la viabilidad. Retornar un JSON con `score` (0-100), `pros`, `contras` y `reasoning`.
*   **`suggest_reply(message: ClientMessage) -> str`**
    *   **Debería hacer:** Tomar un mensaje de un cliente y el contexto del trabajo, y generar una respuesta sugerida profesional y persuasiva.
*   **`generate_proposal_content(job: JobOffer) -> str`**
    *   **Debería hacer:** Generar una "Cover Letter" completa personalizada para la oferta, destacando habilidades relevantes basadas en la descripción.

---

## 4. Adaptadores de Notificación (Mensajería) - PENDIENTE (HU 3.4)

**Ubicación:** `infrastructure/adapters/notification/telegram/adapter.py`
**Estado:** Pendiente

Encargado de comunicar eventos al usuario final.

### `TelegramAdapter` (Futuro)
*   **`notify_opportunity(job: JobOffer, analysis: dict) -> bool`**
    *   **Debería hacer:** Formatear un mensaje atractivo (con emojis, negritas) que muestre el Título, Presupuesto, y el Resumen del análisis de IA. Enviarlo al chat de Telegram configurado.
*   **`notify_message(message: str) -> bool`**
    *   **Debería hacer:** Enviar notificaciones genéricas, errores o confirmaciones de acciones (ej: "Propuesta enviada exitosamente").
