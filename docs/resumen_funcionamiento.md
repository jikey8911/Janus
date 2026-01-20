# Resumen del Funcionamiento de Project Janus (Paso a Paso)

Project Janus automatiza la búsqueda y aplicación a trabajos en Upwork utilizando una **Arquitectura Hexagonal**. El flujo se divide en capas:

## Flujo Principal: Buscar y Analizar (Ya Implementado - HU 2.1)

1.  **Inicio (Trigger)**
    *   El caso de uso `ScanAndAnalyzeJobsUseCase` es invocado (manualmente o por cronjob).
    *   Recibe una consulta de búsqueda (ej. `query="(python OR ai)"`).

2.  **Búsqueda (Puerto de Salida: Upwork)**
    *   El sistema llama a `UpworkPort.search_jobs(query)`.
    *   **Acción:** Se conecta a la API de Upwork y obtiene las ofertas recientes.

3.  **Filtrado y Persistencia (Puerto de Salida: Base de Datos)**
    *   Por cada oferta, el sistema consulta `JobRepository.get_by_upwork_id()`.
    *   **Acción:**
        *   Si existe: Se ignora (evita duplicados).
        *   Si es nueva: Se guarda en la base de datos (`JobRepository.save(job)`).

4.  **Análisis con IA (Puerto de Salida: IA)**
    *   Las ofertas nuevas se envían a `AIServicePort.analyze_job(job)`.
    *   **Acción:** La IA (OpenAI/Gemini) evalúa la descripción, presupuesto y cliente para determinar la viabilidad.
    *   **Resultado:** Se genera un análisis (score, pros/contras).

5.  **Notificación (Puerto de Salida: Notificaciones)**
    *   Si la oferta es viable, se llama a `NotificationPort.notify_opportunity(job, analysis)`.
    *   **Acción:** Envía un mensaje a Telegram con los detalles y el análisis de la IA.

---

## Flujo Secundario: Generar y Enviar Propuesta (En Desarrollo - HU 2.2)

1.  **Solicitud de Propuesta**
    *   Se inicia el caso de uso `GenerateProposalUseCase`.
    *   Toma una oferta existente (`JobOffer`).

2.  **Generación de Contenido (Puerto de Salida: IA)**
    *   Se llama a `AIServicePort.generate_proposal_content(job)`.
    *   **Acción:** La IA redacta una "Cover Letter" personalizada basada en la descripción del trabajo y el perfil del usuario.
    *   **Resultado:** Un borrador de propuesta (`Proposal` con status `draft`).

3.  **Revisión y Envío (Puerto de Salida: Upwork)**
    *   El usuario revisa el borrador (paso manual/intermedio).
    *   Al aprobar, `SubmitProposalUseCase` llama a `UpworkPort.submit_proposal()`.
    *   **Acción:** Se envía la propuesta oficialmente a Upwork.
