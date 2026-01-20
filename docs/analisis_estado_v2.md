# Análisis de Estado y Flujo: Janus V2.0

Este documento contrasta el **Plan de Implementación V2.0** con el código existente, identificando qué está realmente operativo y qué son implementaciones parciales ("placeholders").

## 1. Resumen Ejecutivo
Janus V2.0 ha completado la infraestructura base para un flujo **Unidireccional (Outbound)**: puede buscar, analizar y notificar. Sin embargo, carece de interactividad **(Inbound)** y los "Workers" de ejecución multimeda son conceptos futuros.

## 2. Análisis por Capa (Hexagonal)

### Capa de Dominio (E1)
*   **Estado:** ✅ **Sólido**.
*   **Implementado:** Entidades (`JobOffer`, `Proposal`) y Interfaces (`Ports`) están definidas en `domain/`.
*   **Brecha:** Necesaria actualización de entidades para soportar nuevos tipos de trabajo (V2.0: Contenido, Video) que hoy no existen.

### Capa de Aplicación (E2)
*   **Estado:** ⚠️ **Parcial**.
*   **Implementado:**
    *   `ScanAndAnalyzeJobs`: Funciona completo (Search -> Save -> Analyze -> Notify).
    *   `GenerateProposal`: Genera texto pero *no envía* ni recibe feedback.
*   **Faltante:**
    *   Casos de uso para "Protocolo Científico" (Blueprints, Diagnóstico) no existen en código.
    *   No hay orquestador para decidir qué herramienta usar.

### Capa de Infraestructura (E3 & E4)
*   **Estado:** ⚠️ **En Transición**.

| Adaptador | Estado Código | Estado Real | Notas |
| :--- | :--- | :--- | :--- |
| **MongoDB** | ✅ Implementado | 🟢 Operativo | `MongoJobRepository` guarda y recupera datos. |
| **Upwork** | ✅ Implementado | 🟡 Placeholder | La estructura existe, pero métodos como `search_jobs` retornan listas vacías o simuladas. |
| **Freelancer** | ✅ Implementado | 🟡 Placeholder | Creado a petición (HU 3.2), retorna mocks. Falta lógica real de API. |
| **OpenAI** | ✅ Implementado | 🟢 Operativo | Conectado a la API real. Genera análisis y textos. |
| **Telegram** | ✅ Implementado | 🟢 Operativo | Envía mensajes de salida (Outbound). |
| **Webhooks** | ❌ Inexistente | 🔴 Pendiente | No hay forma de recibir mensajes de Telegram (Inbound). |

---

## 3. Flujo Funcional Actual (Real vs Esperado)

### Flujo A: Radar de Oportunidades
1.  **Cron (`celery`)** dispara `scan_jobs_task`. (✅ Funciona)
2.  **Adaptador** consulta Platforma. (⚠️ Simulado/Mock en código actual).
3.  **Persistencia** guarda en Mongo. (✅ Funciona).
4.  **OpenAI** analiza viabilidad. (✅ Funciona si hay API Key).
5.  **Telegram** notifica al usuario. (✅ Funciona).

**Conclusión Flujo A:** El "esqueleto" funciona de punta a punta, pero no trae datos reales del mundo exterior (Upwork/Freelancer) porque los adaptadores usan credenciales placeholder o no tienen la librería final configurada.

### Flujo B: Protocolo de Ejecución (Nuevo V2.0)
*   Conceptos como "Investigación Perplexity", "Generación de Video", "ElevenLabs" **NO EXISTEN** en el código actual. Son puramente teóricos en el plan.

## 4. Recomendación Inmediata
Para materializar la visión V2.0, el foco debe cambiar de "crear más adaptadores placeholders" a:
1.  **Hacer real el Inbound:** Implementar Webhook de Telegram (Sprint 4) para poder interactuar.
2.  **Conectar Datos Reales:** Reemplazar los mocks de `UpworkAdapter` y `FreelancerAdapter` con llamadas reales a APIs o Scrapers.
