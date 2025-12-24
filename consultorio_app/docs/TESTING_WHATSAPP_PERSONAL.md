# Testing WhatsApp con Número Personal

## 🚀 Plan de Testing

Puedes testear la integración WhatsApp con **tu número personal** sin necesidad de credenciales reales de Meta. Para ello usaremos herramientas de mock y simulación.

Hay dos enfoques:

### **Opción A: Testing Local (SIN WhatsApp real)**
- Simular webhook localmente
- Probar toda la lógica de conversación
- NO requiere credenciales de Meta

### **Opción B: Testing con ngrok + WhatsApp Sandbox (CON respuestas reales)**
- Exponer servidor local vía ngrok
- Conectar a WhatsApp Business Account Sandbox
- Recibir/enviar mensajes REALES a tu número

---

## **Opción A: Testing Local (Recomendado para ahora)**

### 1. Crear script de test manual

```python
# test_whatsapp_local.py
import json
import hmac
import hashlib
from app import create_app
from app.services import ConversationService

app = create_app()

def simulate_webhook(user_phone: str, message: str):
    """Simula un mensaje de WhatsApp sin tocar la API real."""
    
    verify_token = "test-secret"
    
    # 1. Crear payload (estructura de WhatsApp)
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": user_phone,  # Tu número
                        "type": "text",
                        "text": {"body": message}
                    }]
                }
            }]
        }]
    }
    
    body = json.dumps(payload)
    
    # 2. Calcular firma válida
    signature = "sha256=" + hmac.new(
        verify_token.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 3. Simular request HTTP
    with app.test_client() as client:
        response = client.post(
            '/webhooks/whatsapp',
            data=body,
            headers={
                'X-Hub-Signature-256': signature,
                'Content-Type': 'application/json'
            }
        )
    
    return response.status_code, response.get_json()

# Ejecutar test
if __name__ == "__main__":
    print("=== Test 1: Mensaje inicial (DNI) ===")
    status, resp = simulate_webhook("34612345678", "36800456")
    print(f"Status: {status}, Response: {resp}\n")
    
    print("=== Test 2: Nombre ===")
    status, resp = simulate_webhook("34612345678", "Juan")
    print(f"Status: {status}, Response: {resp}\n")
    
    print("=== Test 3: Apellido ===")
    status, resp = simulate_webhook("34612345678", "García")
    print(f"Status: {status}, Response: {resp}\n")
    
    print("=== Test 4: Fecha ===")
    status, resp = simulate_webhook("34612345678", "2025-01-15")
    print(f"Status: {status}, Response: {resp}\n")
    
    print("=== Test 5: Hora ===")
    status, resp = simulate_webhook("34612345678", "14:30")
    print(f"Status: {status}, Response: {resp}\n")
    
    print("✅ Conversación completada")
```

### 2. Ejecutar tests locales

```bash
cd /path/to/consultorio_app

# Test completo del flujo
python test_whatsapp_local.py

# O con pytest
pytest test_whatsapp_local.py -v

# Ver logs detallados
LOG_LEVEL=DEBUG python test_whatsapp_local.py
```

### 3. Verificar logs

```bash
# Ver logs en consola durante test
LOG_LEVEL=DEBUG python test_whatsapp_local.py

# Si configuraste archivo de logs
tail -f logs/whatsapp.log
tail -f logs/odonto.log
```

---

## **Opción B: Testing Real con ngrok + WhatsApp Sandbox**

### Prerequisites

1. **Cuenta Meta Business** (https://business.facebook.com)
2. **WhatsApp Business Account** 
3. **ngrok** para exponer localhost
4. **Tu número personal**

### Paso 1: Configurar WhatsApp Sandbox

1. Ir a: https://developers.facebook.com/
2. Crear o seleccionar App
3. Ir a: **WhatsApp > Getting Started > Test your integration**
4. Copiar valores:
   ```
   WHATSAPP_VERIFY_TOKEN = xxx_yyy_zzz (genéralo tú, ej: "testing-secret-123")
   WHATSAPP_PHONE_NUMBER_ID = 123456789 (está en Sandbox)
   WHATSAPP_ACCESS_TOKEN = EAAxx... (token temporal de test)
   WHATSAPP_BUSINESS_ACCOUNT_ID = xxx (está en settings)
   ```

5. Enviar WhatsApp test a +1 (555) 123-4567 desde tu número para agregarte a la lista de testing

### Paso 2: Instalar y configurar ngrok

```bash
# Descargar ngrok
# https://ngrok.com/download

# Configurar token (opcional pero recomendado)
./ngrok config add-authtoken YOUR_NGROK_TOKEN

# Exponer puerto 5000
./ngrok http 5000
```

Verás algo como:
```
Forwarding    https://abc123def456.ngrok.io -> http://localhost:5000
```

### Paso 3: Registrar webhook en Meta

1. WhatsApp > Getting Started > "Verify and test webhook"
2. URL del webhook: `https://abc123def456.ngrok.io/webhooks/whatsapp`
3. Verify Token: `testing-secret-123` (el que generaste)
4. Hacer clic en **Verify and Save**

### Paso 4: Configurar variables de entorno

```bash
# Crear .env (o actualizar)
cat > .env << EOF
DATABASE_URL=sqlite:///instance/odonto.db
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-123

WHATSAPP_VERIFY_TOKEN=testing-secret-123
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_ACCESS_TOKEN=EAAxx...
WHATSAPP_BUSINESS_ACCOUNT_ID=xxx

LOG_LEVEL=DEBUG
EOF
```

### Paso 5: Iniciar servidor

```bash
python run.py
```

Deberías ver:
```
[OK] Datos por defecto inicializados
[scheduler] Tareas periódicas registradas
[SERVER] Iniciando servidor en http://localhost:5000
Logging configured - Level: DEBUG
 * Running on http://127.0.0.1:5000
```

### Paso 6: Enviar mensaje desde WhatsApp

1. Abre WhatsApp en tu teléfono
2. Búsqueda de contacto: el número que está en el Sandbox (viene con prefijo +1 555)
3. Envía: `36800456` (un DNI de test)
4. Espera respuesta...

### Qué sucede

```
Tu teléfono:
  Usuario: "36800456"
       ↓
   /webhooks/whatsapp (ngrok)
       ↓
   Firma validada ✓
       ↓
   ConversationService: "No encontré tu ficha. Decime tu nombre"
       ↓
   WhatsAppMessageService: envía via API
       ↓
Tu teléfono:
  Bot: "No encontré tu ficha. Decime tu nombre"
```

### Troubleshooting

| Problema | Solución |
|----------|----------|
| "Webhook URL not responding" | Verificar ngrok sigue corriendo + logs en server |
| "Invalid signature" | Checar WHATSAPP_VERIFY_TOKEN coincide en Meta y .env |
| "Unauthorized (401)" | WHATSAPP_ACCESS_TOKEN expirado o incorrecto |
| "No recibes respuesta del bot" | Ver logs: `tail -f logs/whatsapp.log` |
| "Rate limit exceeded" | Esperar 1 minuto, máximo 5 mensajes/minuto |

---

## **Flujo de Conversación de Test**

```
Usuario → Bot → Respuesta esperada

"36800456" 
    → Buscar paciente
    → "No encontré tu ficha. Decime tu nombre"

"Juan"
    → Solicitar apellido
    → "Gracias. Ahora tu apellido."

"García"
    → Crear paciente (si DNI no existe)
    → "Te registré. Indicá la fecha del turno (YYYY-MM-DD)."

"2025-01-15"
    → Validar fecha
    → "Anotado. Indicá la hora (HH:MM)."

"14:30"
    → Crear turno en estado Pendiente
    → "Turno solicitado en estado Pendiente. La doctora confirmará el horario."
```

---

## **Checklist de Security**

Antes de ir a producción:

- [ ] `WHATSAPP_VERIFY_TOKEN` es una cadena aleatoria segura (min 32 caracteres)
- [ ] `WHATSAPP_ACCESS_TOKEN` **NO está** en código (solo en .env)
- [ ] Logs **NO guardan** números de teléfono completos (solo primeros/últimos dígitos)
- [ ] Rate limiting activo (5 msgs/minuto por usuario)
- [ ] HTTPS obligatorio en producción
- [ ] Firma HMAC validada en CADA webhook
- [ ] Errores no exponen detalles internos (JSON responses genéricos)

---

## **Monitoreo en desarrollo**

### Ver todo lo que pasa

```bash
# Terminal 1: Servidor
LOG_LEVEL=DEBUG python run.py

# Terminal 2: Logs de WhatsApp
tail -f logs/whatsapp.log

# Terminal 3: ngrok (si usas sandbox)
./ngrok http 5000
```

### Métricas útiles

```python
# En Python para inspeccionar estado
from app.services import ConversationService
from app.models import Conversation

# Ver conversación activa
convo = Conversation.query.filter_by(channel_user_id="34612345678").first()
print(f"Paso: {convo.paso_actual}")
print(f"Paciente ID: {convo.paciente_id}")
print(f"Expira en: {convo.expira_en}")

# Ver turnos creados
from app.models import Turno
turnos = Turno.query.all()
for turno in turnos:
    print(f"{turno.id}: {turno.paciente.nombre} - {turno.estado}")
```

---

## **Siguientes pasos**

1. ✅ Test local con script
2. ✅ Test con ngrok + Sandbox (tu número personal)
3. ⬜ Validar flujo completo (registro paciente, agendar turno)
4. ⬜ Probar casos edge (teléfono inválido, fecha pasada, etc)
5. ⬜ Integración con UI doctora (confirmación de turnos)

---

## **Tips útiles**

**Para limpiar conversación y reintentar:**
```python
from app.services import ConversationService
ConversationService.reset("34612345678")
# Luego envía un nuevo mensaje para comenzar desde DNI
```

**Para resetear toda la BD de test:**
```bash
rm instance/odonto.db
python run.py  # Recrea BD con datos por defecto
```

**Para ver todos los turnos creados en test:**
```bash
sqlite3 instance/odonto.db "SELECT * FROM turno ORDER BY created_at DESC LIMIT 5;"
```

---

¡Ahora estás listo para testear! Usa **Opción A** (local) para validar la lógica, luego **Opción B** para probar con tu número real.
