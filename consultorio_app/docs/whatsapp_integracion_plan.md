# 🤖 Prompts para Copilot — Diseño de Integración WhatsApp (OdontoApp)

Este documento contiene **todos los prompts recomendados** para usar con GitHub Copilot (Chat / Inline) y guiar el diseño e implementación futura de la integración con **WhatsApp**, respetando la arquitectura actual de OdontoApp.

> 🎯 Objetivo: usar Copilot como **asistente técnico consciente del código**, no como diseñador de arquitectura.

---

## 🧱 BLOQUE 1 — Estado actual del backend

### Prompt 1 — Reutilización de services

```
Analyze the current services architecture in this project.
Which services can already be reused by an external channel like WhatsApp
without modifications?
```

**Respuesta:** Los casos de uso desacoplados en `app/services` ya sirven como core reutilizable: pacientes (buscar/crear/editar), turnos (agendar, editar, cambiar estado, obtener horarios/agenda, listar, eliminar), localidad/obra social (búsqueda/creación), validadores y excepciones en `services/common`. Odontograma no es necesario para WhatsApp pero está libre de Flask, por lo que también es reutilizable si se precisara.

---

### Prompt 2 — Acoplamientos restantes

```
Are there any services that still depend on Flask, HTTP concepts,
or UI-related logic that should be refactored before adding a WhatsApp adapter?
```

**Respuesta:** No hay services con dependencias directas a Flask; la lógica de presentación está en rutas y plantillas. Lo que falta para WhatsApp es añadir un `ConversationService` y un store de estado de conversación (aún no existen) más un parser normalizador de mensajes. No es necesario refactorizar los servicios actuales; solo incorporar estas nuevas piezas.

---

## 🧠 BLOQUE 2 — Estados y modelo de turnos

### Prompt 3 — Transiciones de estado

```
Based on the current Turno states (Pendiente, Confirmado, etc.),
suggest a state transition model that supports turn requests coming from WhatsApp.
Do not implement code, only describe transitions.
```

**Respuesta:** Entrada por WhatsApp crea un turno en `Pendiente` (nunca se confirma automáticamente). Transiciones: `Pendiente -> Confirmado` (solo la doctora desde la UI), `Pendiente -> Cancelado` (desiste), `Confirmado -> Atendido` (consulta realizada), `Confirmado -> NoAtendido` (marcado automático por vencimiento), `Confirmado -> Cancelado` (anulación previa). Estados finales no se reabren.

---

### Prompt 4 — Decisión de modelado

```
Given the current domain model, would it be better to represent
a WhatsApp turn request as:
- a Turno with state 'Pendiente'
- or a separate temporary entity?
Explain pros and cons in this specific project.
```

**Respuesta:**
- Turno `Pendiente`: sencillo, reutiliza servicios y aparece en agenda; riesgo de ruido si la conversación no concluye.
- Entidad temporal (draft): mantiene agenda limpia mientras se conversa; requiere mapping adicional a `Turno` al finalizar.
Recomendación: usar draft en el store conversacional y crear el `Turno` en `Pendiente` solo al confirmar fecha/hora/paciente.

---

## 🧩 BLOQUE 3 — Conversation Service (core, sin WhatsApp)

### Prompt 5 — Diseño del servicio conversacional

```
Design a ConversationService interface for this project.
It should handle a guided conversation to request a turn,
but must not depend on WhatsApp or HTTP.
Describe responsibilities and method signatures.
```

**Respuesta:**
Responsabilidades: guiar el diálogo (identificar paciente, proponer slot, confirmar), validar entradas con servicios de dominio, persistir estado conversacional, producir respuestas neutrales al canal.
Métodos sugeridos:
- `start_conversation(channel_user_id) -> ConversationState`
- `handle_message(channel_user_id, text) -> ConversationReply`
- `get_state(channel_user_id) -> ConversationState`
- `abort(channel_user_id, motivo) -> None`
- `complete(channel_user_id) -> Turno`
Tipos: `ConversationState` (paso, datos recolectados, expiración, intentos), `ConversationReply` (mensaje, opciones, flags de confirmación/error).

---

### Prompt 6 — Persistencia de estado conversacional

```
Which information must be persisted to keep track of a WhatsApp conversation
state across multiple messages in this system?
List fields and explain why each one is needed.
```

**Respuesta:**
- `channel_user_id`: correlacionar mensajes.
- `paciente_id` o `dni_propuesto`: identificar paciente.
- `paso_actual`: saber qué preguntar y validar.
- `fecha_candidate`, `hora_candidate`, `duracion_candidate`: slot propuesto.
- `detalle`: notas opcionales.
- `ultima_interaccion_ts`, `expira_en`: timeouts y limpieza.
- `intentos_actuales`: controlar reintentos/errores.
<!-- Se elimina contexto_mensajes para no guardar texto innecesario -->
- `confirmed`: listo para crear turno.

---

## 🔌 BLOQUE 4 — Adapter WhatsApp (arquitectura limpia)

### Prompt 7 — Ubicación del adapter

```
Given the existing Flask routes and services,
where should a WhatsApp webhook adapter be placed
so it does not leak business logic into the transport layer?
```

**Respuesta:** En un adapter dedicado, p.ej. `app/adapters/whatsapp/` o una ruta `webhooks/whatsapp` mínima que solo parsee/valide firma y delegue al `ConversationService`; nada de lógica de dominio ahí.

---

### Prompt 8 — Responsabilidades del controller

```
What responsibilities should a WhatsAppController have
in a clean architecture setup for this project?
What should it NOT do?
```

**Respuesta:** Debe validar firma/token, parsear payload a DTO neutral, llamar `ConversationService.handle_message`, mapear la respuesta a formato WhatsApp y responder HTTP 200. No debe acceder a ORM ni decidir estados de turnos ni persistir conversación por su cuenta.

---

## 🧪 BLOQUE 5 — Testing sin API externa

### Prompt 9 — Estrategia de testing

```
How can the conversation flow for WhatsApp turn requests
be tested without integrating the real WhatsApp API?
Suggest testing strategies for this backend.
```

**Respuesta:**
- Unit tests de `ConversationService` con fakes de store y servicios de dominio.
- Tests del adapter con payloads webhook de fixture y validación de respuestas.
- Integración con DB de prueba para creación de turnos y solapamientos.
- Tests de firma/seguridad con tokens inválidos y replay.

---

## 🔐 BLOQUE 6 — Seguridad y despliegue (conceptual)

### Prompt 10 — Seguridad del webhook

```
If this application exposes a WhatsApp webhook endpoint,
what security considerations should be addressed
before deploying it publicly?
```

**Respuesta:**
- Verificación de firma/token del proveedor.
- HTTPS obligatorio y posible allowlist de IPs.
- Rate limiting y protección contra replay (timestamp/nonce).
- Sanitizado/log mínimo (evitar datos sensibles completos).
- Alertas/monitor para fallos de verificación y picos.

---

## 🧠 BLOQUE 7 — Prompt maestro (usar al final)

> ⚠️ Usar este prompt **solo cuando los anteriores ya estén respondidos**.

### Prompt 11 — Plan de implementación

```
Given the existing services architecture and state model,
outline a high-level implementation plan for adding WhatsApp turn requests
as an external adapter, without modifying core business logic.
```

**Respuesta:**
1) Crear `ConversationService` + store (tabla conversations) con campos anteriores.
2) Flujo: identificar paciente, proponer slot (`ObtenerHorariosService`), confirmar y crear turno con `AgendarTurnoService`.
3) Adapter/webhook WhatsApp que valide firma y delegue al servicio conversacional.
4) Endpoint Flask `/webhooks/whatsapp` mínimo; sin lógica de dominio.
5) Tests unitarios (conversación) y de adapter con fixtures; integración con DB test.
6) Configurar seguridad (firma, HTTPS), logging y monitoreo.

---

## 🧩 Caso especial — Paciente no registrado que pide turno por WhatsApp

**Propuesta:**
- Durante la conversación, si no se encuentra paciente por DNI/whatsapp, abrir un flujo de alta mínima.
- Alta mínima: nombre, apellido, DNI, teléfono (campos obligatorios actuales) y opcional localidad/obra social si se conocen; validar DNI y no duplicar.
- Crear paciente mediante `CrearPacienteService` antes de agendar; luego continuar con selección de fecha/hora y crear el `Turno` en `Pendiente` (la confirmación siempre la hace la doctora desde la UI).
- Si el usuario abandona antes de completar alta, no crear paciente; mantener el draft en el store conversacional con expiración.
- Riesgos mitigados: evita turnos huérfanos sin paciente, y mantiene agenda limpia porque solo se crea turno una vez que el paciente se registró correctamente.

## 📌 Recomendaciones de uso

* Ejecutar los prompts **en orden**
* No pedir código prematuramente
* Validar cada respuesta contra la arquitectura definida
* Usar Copilot como apoyo, no como diseñador

> WhatsApp debe ser un **canal**, no un nuevo sistema dentro del sistema.

---