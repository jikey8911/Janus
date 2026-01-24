# Plan de Implementación: Sprints 5 y 6 - Estabilización y Gestión de Proyectos

## Objetivo General
Estabilizar el sistema de ofertas, implementar un menú interactivo en Telegram y crear un flujo completo de gestión de proyectos adjudicados con generación automática de planes de implementación.

---

## Sprint 5: Menú de Telegram y Estabilización de Ofertas (1 Semana)

### Objetivo
Implementar una interfaz visual en Telegram con comandos interactivos y corregir el flujo de envío de propuestas a Freelancer.com.

### Historias de Usuario

#### HU 5.1: Menú Visual de Comandos en Telegram
**Descripción:** El bot debe mostrar un menú visual con botones cuando el usuario escribe `/` para facilitar la navegación.

**Tareas:**
1.  Crear `infrastructure/entrypoints/telegram_commands.py` con la clase `TelegramCommandHandler`.
2.  Implementar comandos: `/listar`, `/buscar`, `/enviar`, `/responder`, `/estado`, `/ayuda`.
3.  Integrar el manejador de comandos en el webhook de Telegram.
4.  Pruebas: Verificar que los botones aparecen correctamente en Telegram.

**Criterios de Aceptación:**
- El bot responde a `/listar` con las oportunidades pendientes.
- El bot responde a `/buscar` con un formulario de búsqueda.
- El bot responde a `/estado` con el estado actual del sistema.
- El menú es visual y fácil de usar.

---

#### HU 5.2: Corrección del Adaptador de Freelancer (Bidding Fix)
**Descripción:** Corregir el error de "falta de skills" en el envío de propuestas a Freelancer.com.

**Tareas:**
1.  Crear `infrastructure/adapters/platforms/freelancer/adapter_fixed.py` con mejoras:
    - Validación de credenciales antes de enviar.
    - Manejo robusto de errores en la API.
    - Logging detallado para debugging.
    - Soporte para diferentes tipos de proyectos.
2.  Actualizar el payload del bid para incluir todos los campos requeridos.
3.  Implementar reintentos automáticos en caso de fallo.
4.  Pruebas: Enviar un bid de prueba y verificar que se registra correctamente.

**Criterios de Aceptación:**
- El bid se envía correctamente a Freelancer.com.
- Se registra un log detallado de cada intento.
- En caso de error, se notifica al usuario en Telegram.
- El sistema no intenta enviar bids sin credenciales.

---

#### HU 5.3: Integración de Comandos con Casos de Uso
**Descripción:** Conectar los comandos de Telegram con los Casos de Uso de la aplicación.

**Tareas:**
1.  Actualizar `infrastructure/entrypoints/webhooks.py` para procesar comandos.
2.  Implementar inyección de dependencias para pasar los Casos de Uso al manejador de comandos.
3.  Crear un contenedor de dependencias (`infrastructure/container.py`).
4.  Pruebas: Verificar que `/enviar <job_id>` ejecuta el Caso de Uso correctamente.

**Criterios de Aceptación:**
- Los comandos ejecutan los Casos de Uso correspondientes.
- Las respuestas se envían a Telegram correctamente.
- No hay errores de inyección de dependencias.

---

## Sprint 6: Gestión de Proyectos Adjudicados y Planes de Implementación (1 Semana)

### Objetivo
Implementar un flujo completo para detectar proyectos adjudicados, generar planes de implementación con IA y enviarlos a Telegram para aprobación.

### Historias de Usuario

#### HU 6.1: Detector de Proyectos Adjudicados
**Descripción:** El sistema debe detectar automáticamente cuando un proyecto ha sido adjudicado al usuario.

**Tareas:**
1.  Crear un nuevo Caso de Uso: `AwardedProjectDetectionUseCase` en `application/`.
2.  Implementar polling de Freelancer.com para detectar cambios de estado.
3.  Configurar una tarea de Celery que ejecute el polling cada 5 minutos.
4.  Guardar el estado del proyecto en la base de datos.
5.  Pruebas: Simular un proyecto adjudicado y verificar que se detecta.

**Criterios de Aceptación:**
- El sistema detecta cuando un proyecto pasa a estado "awarded".
- Se registra en la base de datos con timestamp.
- Se ejecuta sin errores cada 5 minutos.

---

#### HU 6.2: Generación de Planes de Implementación
**Descripción:** Cuando se detecta un proyecto adjudicado, el sistema genera automáticamente un plan de implementación basado en la categoría del proyecto.

**Tareas:**
1.  Crear `application/awarded_project_use_case.py` con la clase `AwardedProjectUseCase`.
2.  Implementar generadores de planes para cada categoría:
    - Web Development (5 fases)
    - Mobile Development (3 fases)
    - Data Science (3 fases)
    - Content Creation (3 fases)
    - Translation (1 fase)
    - General (3 fases)
3.  Usar IA para personalizar los planes según los requerimientos específicos.
4.  Guardar el plan en la base de datos.
5.  Pruebas: Generar planes para diferentes categorías y verificar que son coherentes.

**Criterios de Aceptación:**
- Se genera un plan para cada categoría de proyecto.
- El plan incluye fases, tareas y duración estimada.
- La IA personaliza el plan según los requerimientos.
- El plan se guarda correctamente en la BD.

---

#### HU 6.3: Notificación y Aprobación de Planes en Telegram
**Descripción:** El plan de implementación se envía a Telegram para que el usuario lo apruebe antes de enviarlo al cliente.

**Tareas:**
1.  Crear `infrastructure/adapters/notification/telegram/adapter_enhanced.py` con método `notify_implementation_plan`.
2.  Formatear el plan de forma legible en Telegram (con emojis y markdown).
3.  Incluir botones de acción: `/aprobar <job_id>`, `/editar <job_id>`.
4.  Implementar el Caso de Uso `ApproveImplementationPlanUseCase`.
5.  Pruebas: Enviar un plan a Telegram y verificar que se aprueba correctamente.

**Criterios de Aceptación:**
- El plan se muestra correctamente en Telegram.
- El usuario puede aprobar o editar el plan.
- La aprobación se registra en la BD.
- El plan editado se guarda correctamente.

---

#### HU 6.4: Envío del Plan Aprobado a la Plataforma
**Descripción:** Una vez aprobado, el plan se envía automáticamente al cliente en Freelancer.com.

**Tareas:**
1.  Crear un método en `FreelancerAdapter` para enviar mensajes a clientes.
2.  Implementar el Caso de Uso `SendImplementationPlanUseCase`.
3.  Formatear el plan para que sea presentable al cliente.
4.  Registrar el envío en la base de datos.
5.  Pruebas: Enviar un plan a un cliente de prueba y verificar que llega correctamente.

**Criterios de Aceptación:**
- El plan se envía correctamente al cliente.
- Se registra el envío en la BD con timestamp.
- El cliente recibe el plan en Freelancer.com.
- No hay errores de formateo.

---

## Estructura de Archivos Actualizada

```
Janus/
├── application/
│   ├── use_cases.py (existente)
│   ├── awarded_project_use_case.py (NUEVO)
│   └── approval_use_case.py (NUEVO)
├── infrastructure/
│   ├── adapters/
│   │   ├── platforms/
│   │   │   └── freelancer/
│   │   │       ├── adapter.py (existente)
│   │   │       └── adapter_fixed.py (NUEVO)
│   │   └── notification/
│   │       └── telegram/
│   │           ├── adapter.py (existente)
│   │           └── adapter_enhanced.py (NUEVO)
│   ├── entrypoints/
│   │   ├── telegram_commands.py (NUEVO)
│   │   ├── webhooks.py (actualizado)
│   │   └── celery_tasks.py (actualizado)
│   └── container.py (NUEVO)
└── tests/
    └── test_awarded_projects.py (NUEVO)
```

---

## Dependencias Nuevas
- `requests` (ya instalado)
- `celery` (ya instalado)
- `openai` (ya instalado)

---

## Próximos Pasos (Sprint 7)
- Implementar el flujo de respuesta a mensajes de clientes.
- Crear un dashboard de monitoreo.
- Implementar alertas en caso de errores críticos.

---

## Notas de Implementación
1. **Polling vs Webhooks:** Freelancer.com usa polling (no webhooks), así que se ejecutará cada 5 minutos.
2. **Manejo de Errores:** Todos los adaptadores deben registrar errores detallados para debugging.
3. **Testing:** Se recomienda usar mocks para las APIs externas en los tests unitarios.
4. **Seguridad:** Nunca loguear credenciales o tokens sensibles.
