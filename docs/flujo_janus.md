# Flujo Completo de Project Janus

Este documento describe los flujos de trabajo principales del sistema Janus y el estado de implementación de cada paso al final del **Sprint 3**.

---

## 1. Flujo: Detección y Análisis de Oportunidades
**Objetivo:** Encontrar trabajos relevantes, analizarlos y notificar al usuario.

### Paso a Paso:
1.  **Trigger (Disparador):**
    *   *Diseño:* Una tarea programada (Celery Beat) se ejecuta cada 10 minutos.
    *   *Estado:* ✅ **Implementado**. (Configurado en `infrastructure/celery_app.py`, tarea `scan_jobs_task`).

2.  **Búsqueda (Search):**
    *   *Acción:* El sistema consulta la plataforma (Upwork/Freelancer) buscando términos clave (ej: "Python", "Automation").
    *   *Estado:* ✅ **Implementado**.
        *   `UpworkAdapter`: Estructura lista (usa `python-upwork`).
        *   `FreelancerAdapter`: Estructura lista.

3.  **Filtrado y Persistencia (Save):**
    *   *Acción:* Se verifica si la oferta ya existe en la base de datos local. Si es nueva, se guarda.
    *   *Estado:* ✅ **Implementado**.
        *   `MongoJobRepository`: Guarda ofertas evitando duplicados (Upsert).

4.  **Análisis Inteligente (Analyze):**
    *   *Acción:* Se envía la descripción del trabajo a la IA (OpenAI) para evaluar su viabilidad (Score 0-100), Pros y Contras.
    *   *Estado:* ✅ **Implementado**.
        *   `OpenAIAdapter`: Envía prompts a GPT-4o-mini y retorna JSON estructurado.

5.  **Notificación (Notify):**
    *   *Acción:* Si el score es alto, se envía una alerta al usuario vía Telegram con el resumen.
    *   *Estado:* ✅ **Implementado**.
        *   `TelegramAdapter`: Envía mensajes formateados con Markdown y Emojis.

---

## 2. Flujo: Generación de Propuestas
**Objetivo:** Crear un borrador de propuesta personalizado para una oferta atractiva.

### Paso a Paso:
1.  **Trigger (Disparador):**
    *   *Diseño:* El usuario solicita generar propuesta (comando manual) o el sistema lo hace automáticamente para ofertas con Score > 90.
    *   *Estado:* ⚠️ **Parcialmente Implementado**.
        *   La lógica (`GenerateProposalUseCase`) existe y funciona programáticamente.
        *   *Falta:* El mecanismo para que el usuario dispare esto desde Telegram (Bot interactivo - Sprint 4).

2.  **Generación de Contenido (Drafting):**
    *   *Acción:* La IA redacta una "Cover Letter" personalizada basada en la descripción del trabajo y el perfil del freelancer.
    *   *Estado:* ✅ **Implementado**.
        *   `OpenAIAdapter.generate_proposal_content`: Genera el texto persuasivo.

3.  **Persistencia del Borrador:**
    *   *Acción:* Se guarda la propuesta en estado `draft` en la base de datos.
    *   *Estado:* ✅ **Implementado**.
        *   `MongoProposalRepository`: Guarda la propuesta generada.

4.  **Notificación de Borrador:**
    *   *Acción:* Se avisa al usuario: "Propuesta generada para oferta X. ID: 123".
    *   *Estado:* ✅ **Implementado**.

---

## 3. Flujo: Envío de Propuestas (Submission)
**Objetivo:** Enviar la propuesta final a la plataforma.

### Paso a Paso:
1.  **Revisión y Aprobación:**
    *   *Diseño:* El usuario revisa el borrador y da el "OK" (comando `/approve 123`).
    *   *Estado:* ❌ **No Implementado** (Sprint 4).

2.  **Envío (Submit):**
    *   *Acción:* El sistema usa el adaptador de plataforma para postularse realmente.
    *   *Estado:* ⚠️ **Parcialmente Implementado**.
        *   El adaptador (`UpworkAdapter.submit_proposal`) tiene el método, pero falta integrarlo en un Caso de Uso `SubmitProposalUseCase` completo y conectarlo al comando del usuario.

---

## Resumen de Progreso
| Componente | Estado | Notas |
| :--- | :--- | :--- |
| **Dominio (Lógica Core)** | ✅ Listo | Entidades y Puertos definidos. |
| **Casos de Uso** | ✅ Listo | Buscar, Analizar, Generar Borrador. |
| **Persistencia (DB)** | ✅ Listo | MongoDB conectado y funcionando. |
| **Conexión Externa** | ✅ Listo | Adaptadores para OpenAI, Telegram, Upwork/Freelancer. |
| **Interacción Usuario** | ❌ Pendiente | Falta Bot de Telegram interactivo (Webhooks) - **Objetivo Sprint 4**. |
| **Despliegue** | ❌ Pendiente | Falta ponerlo a correr en servidor real 24/7. |
