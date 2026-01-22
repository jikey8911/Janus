# 🦅 Project Janus V2.1 - Sistema de Freelancing Autónomo

Janus es una plataforma basada en **Arquitectura Hexagonal** diseñada para automatizar el ciclo de vida del freelancing: desde la detección de oportunidades y el análisis con IA, hasta la generación de propuestas y la mensajería con clientes.

## 🧠 Arquitectura
El proyecto sigue rigurosamente los principios de **Clean Architecture**:
- **Domain**: Entidades y reglas de negocio puras (`JobOffer`, `Proposal`).
- **Application**: Casos de uso orquestadores (`ScanJobs`, `GenerateProposal`).
- **Infrastructure**: Adaptadores para el mundo exterior (Telegram, OpenAI, MongoDB, Upwork).

## 🚀 Servicios Principales
1.  **Inbound Listener (Webhooks/Polling)**: Escucha eventos de plataformas (Freelancer/Upwork).
2.  **Brain (Celery Workers)**: Procesa tareas pesadas como análisis de IA y generación de contenido.
3.  **Interface (Telegram Bot)**: Interfaz de comando y control para el usuario humano.

---

## 🛠️ Instalación y Configuración

### 1. Prerrequisitos
- Python 3.10+
- MongoDB (Persistencia)
- Redis (Broker de Mensajes)

### 2. Configuración de Entorno
Crea un archivo `.env` en la raíz basado en el ejemplo:
```bash
# Plataformas
UPWORK_API_KEY=...
FREELANCER_API_TOKEN=...

# IA
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini

# Infraestructura
DATABASE_URL=mongodb://localhost:27017/janus_db
REDIS_URL=redis://localhost:6379/0

# Notificaciones
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 3. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

---

## 🖥️ Ejecución en Desarrollo (Dev Services)

¡Nuevo! Ahora puedes iniciar todos los servicios (Bot, Worker, Beat) con un solo comando:

```bash
python run.py
```

Esto abrirá los 3 procesos necesarios. Para detenerlos, simplemente presiona `Ctrl+C`.

### Opcional: Webhook Server (FastAPI)
Si vas a recibir eventos vía Webhook.
```bash
uvicorn infrastructure.entrypoints.webhooks:app --reload --port 8000
```

---

## 🚢 Despliegue (Deployer)

Para desplegar en entorno productivo (Deployer), se recomienda utilizar contenedores Docker.

### Pasos de Despliegue:
1.  **Construir Imagen**:
    Asegúrate de tener el `Dockerfile` configurado (pendiente de creación en carpeta `deployer/`).
2.  **Orquestación**:
    Utiliza `docker-compose up -d` para levantar los servicios definidos: `janus-worker`, `janus-beat`, `janus-bot`.
3.  **Verificación**:
    Revisar logs de contenedores:
    ```bash
    docker logs janus-bot
    ```

---

## 🧪 Testing
Para ejecutar las pruebas unitarias y de integración:
```bash
pytest tests/
```
Para simular un flujo completo de demostración:
```bash
python tests/demo_flow_v3.py
```
