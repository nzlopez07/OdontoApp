# Implementación WhatsApp — Resumen Técnico

## 📋 Completado en esta sesión

### 1. **Backend Core** ✅
- `app/models/conversation.py`: Modelo SQLAlchemy para almacenar estado conversacional
- `app/services/conversacion/conversation_service.py`: Orquesta flujo DNI → registro → fecha/hora → crear Turno
- `app/services/conversacion/__init__.py`: Exports ConversationService y ConversationReply
- `app/services/__init__.py`: Actualizado para exportar servicios de conversación

### 2. **WhatsApp Adapter** ✅
- `app/adapters/whatsapp/webhook_handler.py`:
  - `WhatsAppWebhookValidator`: Validación HMAC-SHA256 de firmas
  - `WhatsAppPayloadParser`: Extrae mensajes del payload de WhatsApp
  - `WhatsAppMessageFormatter`: Formatea respuestas
  - `WhatsAppWebhookHandler`: Orquesta validación → parsing → delegación a ConversationService
- `app/adapters/whatsapp/__init__.py`: Exports clases del adapter

### 3. **Rutas Flask** ✅
- `app/routes/webhooks.py`:
  - `GET /webhooks/whatsapp`: Challenge inicial (verificación)
  - `POST /webhooks/whatsapp`: Procesa mensajes y eventos
- `app/routes/__init__.py`: Registrado blueprint en create_app()

### 4. **Configuración** ✅
- `.env.example`: Plantilla con todas las variables necesarias (tokens, teléfono, etc)
- Variables requeridas documentadas:
  - `WHATSAPP_VERIFY_TOKEN`: token secreto para validar webhooks
  - `WHATSAPP_ACCESS_TOKEN`: token para enviar mensajes
  - `WHATSAPP_PHONE_NUMBER_ID`: ID del teléfono business

### 5. **Servicios mejorados** ✅
- `app/services/turno/agendar_turno_service.py`:
  - Ahora acepta parámetro `estado` (default='Confirmado')
  - Soporta `estado='Pendiente'` para turnos de WhatsApp
  - Sin cambios en lógica de solapamiento ni validación

### 6. **Tests** ✅
- `tests/adapters/test_whatsapp_adapter.py`:
  - Tests de validación HMAC
  - Tests de parsing de payloads
  - Tests de handler completo
  - Tests de challenge inicial
  - Cobertura: firma válida/inválida, status updates, JSON malformado, etc

### 7. **Tareas periódicas** ✅
- `app/scheduler.py`:
  - `cleanup_expired_conversations()`: Elimina conversaciones expiradas
  - `register_background_tasks(app)`: Registra tareas con APScheduler
  - Integrado en `run.py` al iniciar servidor
  - **Nota**: APScheduler opcional (intenta importar, avisa si falta)

### 8. **Documentación** ✅
- `docs/WHATSAPP_SETUP.md`: Guía completa de setup y próximos pasos
- Resumen de arquitectura y seguridad

---

## 🔧 Estructura de directorios

```
app/
  ├─ adapters/                   # NUEVO: Canales externos
  │   └─ whatsapp/
  │       ├─ __init__.py
  │       └─ webhook_handler.py
  ├─ models/
  │   ├─ conversation.py         # NUEVO: Almacen conversación
  │   └─ __init__.py             # Actualizado
  ├─ routes/
  │   ├─ webhooks.py             # NUEVO: Rutas /webhooks/*
  │   └─ __init__.py             # Actualizado
  ├─ services/
  │   ├─ conversacion/
  │   │   ├─ __init__.py         # NUEVO: Exports
  │   │   └─ conversation_service.py  # NUEVO: Lógica conversacional
  │   ├─ turno/
  │   │   └─ agendar_turno_service.py # ACTUALIZADO: soporta estado param
  │   └─ __init__.py             # ACTUALIZADO: incluye conversation imports
  ├─ scheduler.py                # NUEVO: Tareas periódicas
  └─ __init__.py                 # ACTUALIZADO: registra webhooks blueprint
tests/
  ├─ adapters/
  │   ├─ __init__.py
  │   └─ test_whatsapp_adapter.py # NUEVO: Tests del adapter
  └─ __init__.py
.env.example                      # NUEVO: Plantilla de configuración
docs/
  └─ WHATSAPP_SETUP.md           # NUEVO: Guía de setup
```

---

## 🔐 Flujo de seguridad

```
WhatsApp Cloud
    ↓ (POST con firma HMAC-SHA256 en X-Hub-Signature-256)
/webhooks/whatsapp
    ↓
WhatsAppWebhookValidator.validate_signature()
    ✓ Si válida → continuar
    ✗ Si inválida → retornar 401
    ↓
WhatsAppPayloadParser.extract_message_info()
    ✓ Si mensaje válido → extraer (channel_user_id, texto)
    ✗ Si status update → ignorar (retornar 200)
    ✗ Si malformado → retornar 400
    ↓
ConversationService.handle_message(channel_user_id, texto)
    ↓ (estado conversacional en DB)
    ↓
ConversationReply (mensaje, paso, done)
    ↓
HTTP 200 + ACK
```

---

## ⚙️ Requisitos para producción

### Instalables con pip
```bash
pip install apscheduler  # Para cleanup automático (opcional pero recomendado)
pip install requests     # Para enviar mensajes vía WhatsApp API (cuando se implemente)
```

### Configuración obligatoria
1. Copiar `.env.example` → `.env`
2. Llenar tokens de Meta/WhatsApp Business Account
3. Configurar `WHATSAPP_VERIFY_TOKEN` (elige valor seguro)
4. HTTPS en producción (WhatsApp solo acepta HTTPS)

### Pasos finales no implementados (próxima sesión)
1. **Envío de mensajes**: Implementar background task para enviar ConversationReply vía WhatsApp API
2. **Logging/Auditoría**: Agregar logs de webhooks (firma inválida, errores)
3. **Rate limiting**: Proteger endpoint contra abuso
4. **Validación E.164**: Verificar que teléfono sea formato correcto
5. **Retry logic**: Reintentar envío si falla la API

---

## 🧪 Cómo testear

### Tests unitarios
```bash
# Instalar pytest si no está
pip install pytest

# Ejecutar tests del adapter
pytest tests/adapters/test_whatsapp_adapter.py -v
```

### Tests manuales (sin WhatsApp real)
```python
# En Python REPL:
from app.adapters.whatsapp import WhatsAppWebhookHandler
import json, hmac, hashlib

handler = WhatsAppWebhookHandler("test-secret")
payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": "34612345678",
                    "type": "text",
                    "text": {"body": "Hola"}
                }]
            }
        }]
    }]
}
body = json.dumps(payload)
sig = "sha256=" + hmac.new(b"test-secret", body.encode(), hashlib.sha256).hexdigest()

from app.services import ConversationService
result, status = handler.handle_webhook(body, sig, ConversationService)
print(result, status)  # Debe ser ({"status": "received"}, 200)
```

---

## 📊 Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                     WhatsApp Cloud / Cliente                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS POST
                           ↓
          ┌────────────────────────────────────┐
          │  /webhooks/whatsapp (Flask Route)  │
          └────────┬───────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ↓                     ↓
   GET (Challenge)    POST (Message/Event)
        │                     │
        │                  [Firma]
        │                     │ WhatsAppWebhookValidator
        │                     ↓
        │                  [JSON]
        │                     │ WhatsAppPayloadParser
        │                     ↓
        │              [channel_user_id, text]
        │                     │ ConversationService
        │                     ↓
        │              [DNI lookup]
        │                     ├─→ [Existe] → Solicitar fecha
        │                     └─→ [No existe] → Solicitar nombre
        │                              │
        │                              ↓
        │                         [Registrar paciente]
        │                              │
        │                              ↓
        │                    [Agendar turno en Pendiente]
        │                    (AgendarTurnoService)
        │                              │
        │                              ↓
        │                    [Actualizar Conversation]
        │                              │
        └──────────────────────────────┘
                           │
                ┌──────────┘
                ↓
        [ConversationReply]
             (mensaje, paso, done)
                │
        [HTTP Response]
        ├─ GET: "OK" (200) o "Forbidden" (403)
        └─ POST: {"status": "received"} (200), {"error": "..."} (401/400/500)
```

---

## 🚀 Próximas sesiones

**Sesión N+1: Envío de mensajes**
- Implementar función para enviar ConversationReply vía WhatsApp API
- Usar background task (Celery o APScheduler)
- Manejo de errores (timeout, rate limit, etc)

**Sesión N+2: Monitoreo y logging**
- Agregar logs estructurados de webhooks
- Métricas (mensajes procesados, conversaciones completadas)
- Alertas de errores

**Sesión N+3: Optimizaciones**
- Rate limiting
- Caché de pacientes frecuentes
- Validación E.164 de teléfono
- Tests de carga

---

## 📝 Notas importantes

- **No auto-confirma**: Turnos desde WhatsApp siempre en estado Pendiente; confirmación solo desde UI doctora
- **Minimal storage**: Solo se guardan datos necesarios (DNI, fecha/hora, paso conversacional); sin contexto_mensajes
- **Channel-agnostic**: ConversationService no depende de WhatsApp; podría reutilizarse para Telegram, SMS, etc
- **Validación de firma**: Crítico para seguridad; nunca procesa webhooks sin firma válida
- **Expiración**: Conversaciones se limpian automáticamente después de 30 min de inactividad

---

Toda la integración está lista para recibir webhooks. El siguiente paso es implementar el envío de mensajes vía WhatsApp API.
