# Plan de Implementación: Project Janus (Arquitectura Hexagonal)

## Visión del Proyecto
Refactorizar "Project Janus" a una Arquitectura Hexagonal (Puertos y Adaptadores) para lograr independencia de la tecnología, facilitar el testing y permitir la escalabilidad al desacoplar la lógica de negocio de la infraestructura (Upwork, Telegram, Base de Datos, IA).

## Épicas (Capas de la Arquitectura Hexagonal)

| Épica | Nombre | Descripción |
| :--- | :--- | :--- |
| **E1** | **Dominio y Puertos** | Define las entidades de negocio (JobOffer, Proposal) y los contratos (Puertos) que la aplicación usará para interactuar con el mundo exterior. |
| **E2** | **Aplicación y Casos de Uso** | Contiene la lógica de negocio central (Casos de Uso) que orquesta el flujo de trabajo (Buscar, Analizar, Proponer). |
| **E3** | **Infraestructura y Adaptadores** | Implementa los Puertos definidos en E1. Contiene los adaptadores concretos para la Base de Datos, Upwork, Telegram e IA. |
| **E4** | **Integración y Despliegue** | Conecta los adaptadores a la capa de aplicación (inyección de dependencias) y configura el entorno de producción (Webhooks, CI/CD). |

---

## Sprints y Tareas Detalladas

### Sprint 1: Capa de Dominio y Puertos (2 Semanas)
*   **Objetivo:** Definir el núcleo inmutable del negocio y los contratos de interacción.
*   **Historias de Usuario:**
    *   **HU 1.1: Definir Entidades de Dominio:** Crear clases inmutables para `JobOffer`, `Proposal`, `ClientMessage`.
    *   **HU 1.2: Definir Puertos de Salida (Base de Datos):** Crear interfaces (`JobRepository`, `ProposalRepository`) para guardar y recuperar datos.
    *   **HU 1.3: Definir Puertos de Salida (Servicios Externos):** Crear interfaces (`UpworkPort`, `AIServicePort`, `NotificationPort`) para servicios externos.
    *   **HU 1.4: Refactorizar Estructura de Directorios:** Mover el código existente a la nueva estructura hexagonal.

### Sprint 2: Capa de Aplicación (Casos de Uso y Orquestación) (2 Semanas)
*   **Objetivo:** Implementar la lógica de negocio central (Casos de Uso) que orquesta el flujo de trabajo.
*   **Historias de Usuario:**
    *   **HU 2.1: Caso de Uso "Buscar y Analizar Ofertas":** Implementar la lógica que llama a `UpworkPort` y luego a `AIServicePort`.
    *   **HU 2.2: Caso de Uso "Generar Propuesta":** Implementar la lógica que usa el análisis de la IA para generar una propuesta y la guarda usando `ProposalRepository`.
    *   **HU 2.3: Caso de Uso "Notificar Oportunidad":** Implementar la lógica que usa `NotificationPort` para enviar la propuesta a Telegram.
    *   **HU 2.4: Integrar Casos de Uso con Celery:** Conectar los Casos de Uso a las tareas asíncronas.

### Sprint 3: Capa de Infraestructura (Adaptadores Concretos) (2 Semanas)
*   **Objetivo:** Implementar los adaptadores concretos para los servicios externos.
*   **Historias de Usuario:**
    *   **HU 3.1: Adaptador de Base de Datos (SQLAlchemy):** Implementar `JobRepository` y `ProposalRepository` usando SQLAlchemy.
    *   **HU 3.2: Adaptador de Upwork:** Implementar `UpworkPort` usando la librería `python-upwork`.
    *   **HU 3.3: Adaptador de IA (OpenAI):** Implementar `AIServicePort` usando la librería `openai`.
    *   **HU 3.4: Adaptador de Notificación (Telegram):** Implementar `NotificationPort` usando la API de Telegram.

### Sprint 4: Integración, Webhooks y Despliegue Final (2 Semanas)
*   **Objetivo:** Conectar todos los componentes, implementar los Puertos de Entrada (Webhooks) y finalizar el CI/CD.
*   **Historias de Usuario:**
    *   **HU 4.1: Puerto de Entrada (Telegram Webhook):** Implementar el endpoint de FastAPI que recibe mensajes de Telegram y llama al Caso de Uso "Procesar Respuesta".
    *   **HU 4.2: Caso de Uso "Procesar Respuesta":** Implementar la lógica para manejar los comandos "ENVIAR", "RESPONDER" y las ediciones.
    *   **HU 4.3: Inyección de Dependencias:** Configurar la inyección de los adaptadores concretos en los Casos de Uso.
    *   **HU 4.4: Despliegue Final:** Ajustar la configuración de Render para el entorno de producción y verificar el CI/CD.

---
