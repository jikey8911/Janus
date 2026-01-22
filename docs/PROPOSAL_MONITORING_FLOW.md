"""
Flujo de Estados de Propuesta Post-Envío

Después de enviar una propuesta a la plataforma (Freelancer/Upwork),
el sistema debe monitorear y gestionar los siguientes estados:

## Estados de Propuesta

1. **draft** - Propuesta creada, pendiente de aprobación
2. **approved** - Aprobada por usuario, lista para enviar
3. **submitted** - Enviada a la plataforma
4. **pending_award** - Esperando adjudicación del cliente
5. **awarded** - Proyecto adjudicado (ganamos)
6. **rejected_by_client** - Cliente rechazó la propuesta
7. **withdrawn** - Propuesta retirada por nosotros
8. **expired** - Propuesta expiró sin respuesta

## Flujo Post-Envío

```
Usuario aprueba en Telegram
         ↓
Estado: approved
         ↓
Enviar a plataforma (FreelancerAdapter.submit_proposal)
         ↓
Estado: submitted
         ↓
┌────────────────────────────────────────┐
│  MONITOREO CONTINUO (Celery Beat)     │
│  - Cada 5 minutos                      │
│  - Verificar estado en plataforma      │
│  - Detectar mensajes nuevos            │
└────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  EVENTOS POSIBLES:                      │
│                                         │
│  1. Cliente envía mensaje               │
│     → Notificar a Telegram              │
│     → Estado: pending_award             │
│     → Esperar respuesta del usuario     │
│                                         │
│  2. Proyecto adjudicado                 │
│     → Estado: awarded                   │
│     → Notificar éxito                   │
│     → Iniciar fase de producción        │
│                                         │
│  3. Propuesta rechazada                 │
│     → Estado: rejected_by_client        │
│     → Notificar y archivar              │
│                                         │
│  4. Sin respuesta (timeout)             │
│     → Estado: expired                   │
│     → Archivar                          │
└─────────────────────────────────────────┘
```

## Implementación Requerida

### 1. Actualizar Entidad Proposal
```python
@dataclass
class Proposal:
    id: Optional[int]
    job_offer_id: int
    content: str
    status: str  # draft, approved, submitted, pending_award, awarded, rejected_by_client, withdrawn, expired
    platform_proposal_id: Optional[str]  # ID de la propuesta en la plataforma
    submitted_at: Optional[datetime]
    last_checked_at: Optional[datetime]
    awarded_at: Optional[datetime]
```

### 2. Crear Celery Task de Monitoreo
```python
@shared_task(name="monitor_submitted_proposals")
def monitor_submitted_proposals():
    """
    Ejecutado cada 5 minutos.
    Verifica estado de propuestas enviadas.
    """
    # 1. Obtener propuestas con estado 'submitted' o 'pending_award'
    # 2. Para cada propuesta:
    #    - Consultar estado en plataforma
    #    - Verificar mensajes nuevos
    #    - Actualizar estado si cambió
    #    - Notificar eventos a Telegram
```

### 3. Handler para Mensajes del Cliente
```python
async def handle_client_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cuando el cliente envía un mensaje sobre la propuesta.
    """
    # 1. Mostrar mensaje del cliente
    # 2. Proporcionar botones:
    #    - Responder
    #    - Ver propuesta original
    #    - Retirar propuesta
```

### 4. Actualizar handle_approve_proposal
```python
async def handle_approve_proposal(query, proposal_id: str):
    # 1. Obtener propuesta de DB
    # 2. Enviar a plataforma
    # 3. Actualizar estado a 'submitted'
    # 4. Guardar platform_proposal_id
    # 5. Notificar éxito
    # 6. Iniciar monitoreo automático
```

## Notificaciones a Telegram

### Mensaje del Cliente Recibido
```
📬 MENSAJE DEL CLIENTE

Proyecto: [título]
Propuesta ID: [id]

Cliente dice:
"[contenido del mensaje]"

[Botón: Responder]
[Botón: Ver Propuesta]
[Botón: Retirar]
```

### Proyecto Adjudicado
```
🎉 ¡PROYECTO ADJUDICADO!

Proyecto: [título]
Presupuesto: [monto]
Cliente: [nombre]

La propuesta fue aceptada.
Iniciando fase de producción...

[Botón: Ver Detalles]
[Botón: Iniciar Trabajo]
```

### Propuesta Rechazada
```
❌ PROPUESTA RECHAZADA

Proyecto: [título]
Motivo: [si está disponible]

[Botón: Ver Análisis]
[Botón: Archivar]
```

## Archivos a Modificar

1. `domain/entities.py` - Añadir campos a Proposal
2. `infrastructure/entrypoints/celery_tasks.py` - Añadir monitor_submitted_proposals
3. `infrastructure/entrypoints/telegram_bot.py` - Añadir handlers de mensajes
4. `infrastructure/adapters/platforms/freelancer/adapter.py` - Métodos para verificar estado
5. `application/use_cases.py` - Caso de uso MonitorProposalsUseCase

## Prioridad de Implementación

- [ ] Sprint Actual: Actualizar flujo de aprobación (no pasar a producción)
- [ ] Próximo Sprint: Implementar monitoreo de propuestas
- [ ] Futuro: Gestión de mensajes bidireccional
- [ ] Futuro: Inicio automático de fase de producción
"""
<parameter name="Complexity">4
