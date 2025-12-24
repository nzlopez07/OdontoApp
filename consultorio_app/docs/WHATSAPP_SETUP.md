# Guía: Completar integración WhatsApp

## Resumen de lo implementado

### ✅ Backend core
1. **Conversation Model** (`app/models/conversation.py`): almacena estado conversacional.
2. **ConversationService** (`app/services/conversacion/conversation_service.py`): orquesta flujo DNI → nombre → fecha/hora → crear Turno en Pendiente.
3. **AgendarTurnoService actualizado**: soporta parámetro `estado='Pendiente'` para turnos de WhatsApp.
4. **WhatsApp Adapter** (`app/adapters/whatsapp/webhook_handler.py`):
   - Valida firma HMAC-SHA256
   - Parsea payloads de WhatsApp
   - Delega al ConversationService
   - Formatea respuestas

### ✅ Rutas
- `POST /webhooks/whatsapp`: recibe mensajes y eventos
- `GET /webhooks/whatsapp`: challenge inicial para verificación

### ⚙️ Configuración requerida
Copia `.env.example` a `.env` y completa valores:
- `WHATSAPP_VERIFY_TOKEN`: token secreto (elige uno seguro)
- `WHATSAPP_ACCESS_TOKEN`: token de acceso para enviar mensajes (desde Meta Cloud)
- `WHATSAPP_PHONE_NUMBER_ID`: ID del teléfono business (desde Meta)

---

## Pasos finales (no implementados aún)

### 1️⃣ Envío de mensajes (background)
El webhook recibe mensajes pero **no envía respuestas automáticamente** (por seguridad/diseño).
Para enviar, necesitas:

```python
# Opción A: En background con Celery/APScheduler
@celery.task
def send_whatsapp_message(phone_number, message_text):
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    url = f"https://graph.instagram.com/v17.0/{phone_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message_text}
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200

# Opción B: Síncrono en el handler (más simple para inicio)
# Pero cuidado con timeouts del webhook
```

### 2️⃣ Cleanup de conversaciones expiradas
Agregar tarea periodica (p.ej. con APScheduler):

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def cleanup_expired_conversations():
    """Elimina conversaciones expiradas."""
    session = DatabaseSession.get_instance().session
    now = datetime.utcnow()
    
    expired = Conversation.query.filter(Conversation.expira_en < now).all()
    for convo in expired:
        session.delete(convo)
    session.commit()

# En create_app():
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_conversations, 'interval', minutes=5)
scheduler.start()
```

### 3️⃣ Logging y monitoreo
Agregar logs en webhook para auditoría:

```python
import logging

logger = logging.getLogger(__name__)

# En handle_webhook():
logger.info(f"WhatsApp msg from {channel_user_id}: {text[:50]}...")
logger.warning(f"Invalid signature from {request.remote_addr}")
```

### 4️⃣ Tests
Crear `tests/test_whatsapp_adapter.py`:

```python
import json
import hmac
import hashlib
from app.adapters.whatsapp import WhatsAppWebhookHandler

def test_webhook_validation():
    handler = WhatsAppWebhookHandler("test-token")
    body = json.dumps({"object": "whatsapp_business_account"})
    
    # Válida
    valid_sig = "sha256=" + hmac.new(
        b"test-token", body.encode(), hashlib.sha256
    ).hexdigest()
    result, status = handler.handle_webhook(body, valid_sig, MockConversationService())
    assert status == 200
    
    # Inválida
    invalid_sig = "sha256=bad"
    result, status = handler.handle_webhook(body, invalid_sig, MockConversationService())
    assert status == 401
```

### 5️⃣ Considerar flujos edge-case
- Usuario envía medio (foto/audio): parsear o rechazar con "Solo acepto texto"
- Usuario intenta agendar fecha pasada: validar en ConversationService
- Usuario abandona a mitad (timeout): cleanup + reintentó desde DNI
- Concurrencia: ¿múltiples mensajes simultáneamente? → usar locks en store

---

## Arquitectura final

```
WhatsApp Cloud →
    ↓
[GET/POST /webhooks/whatsapp]
    ↓
WhatsAppWebhookHandler
    ├─ Valida firma ✓
    ├─ Parsea payload ✓
    ↓
ConversationService
    ├─ Busca/crea paciente
    ├─ Recolecta fecha/hora
    ├─ Llama AgendarTurnoService
    ↓
[Conversation table] (state)
↓
[Turno table] (estado = Pendiente)
    ↓
UI doctora: confirma/cancela/edita turno
```

## Seguridad (checklist antes de producción)

- [ ] `WHATSAPP_VERIFY_TOKEN` en .env, nunca en código
- [ ] `WHATSAPP_ACCESS_TOKEN` rotado periódicamente
- [ ] HTTPS obligatorio en producción
- [ ] Rate limiting en /webhooks/whatsapp (1 req/sec por usuario)
- [ ] Logs sin guardar mensajes completos (privacidad)
- [ ] Validar que teléfono sea formato E.164 (p.ej. +34612345678)
- [ ] Tests de seguridad (firma inválida, replay, inyección JSON)

---

## Próximos pasos en orden

1. Copiar `.env.example` → `.env` y llenar tokens (en paralelo: pedirle a cliente)
2. Implementar envío de mensajes (background task)
3. Agregar tests unitarios del adapter
4. Agregar cleanup de conversaciones expiradas
5. Desplegar a staging + validar con números de prueba
6. Monitoreo/alertas en producción

---

## Contacto/Dudas
Revisar `whatsapp_integracion_plan.md` para detalles de diseño.
