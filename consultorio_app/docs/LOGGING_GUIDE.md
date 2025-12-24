# 📋 Guía del Sistema de Logging - OdontoApp

## 🎯 Objetivo

Proporcionar visibilidad técnica del sistema para soporte remoto **sin comprometer la privacidad de datos clínicos**.

---

## 🔐 Principio Fundamental: Privacidad por Diseño

### ❌ NUNCA loggear:
- Nombres de pacientes
- DNI completos
- Diagnósticos o tratamientos
- Montos específicos (excepto en eventos de creación/eliminación)
- Direcciones, teléfonos, emails completos
- Contraseñas o tokens de acceso

### ✅ SÍ loggear:
- IDs numéricos (paciente_id=123)
- Eventos técnicos (creado, actualizado, eliminado)
- Estados de entidades (Pendiente, Confirmado, etc.)
- Errores con stack traces (sin datos personales)
- Métricas agregadas (total de turnos, prestaciones)
- Eventos de seguridad (login, logout, permisos denegados)

---

## 📁 Archivos de Log

Ubicación: `logs/`

| Archivo | Propósito | Rotación | Backups |
|---------|-----------|----------|---------|
| `app.log` | Log principal de la aplicación | 10 MB | 10 archivos |
| `errors.log` | Solo errores y excepciones | 10 MB | 5 archivos |
| `security.log` | Login, logout, accesos denegados | 5 MB | 5 archivos |
| `whatsapp.log` | Integración con WhatsApp | 5 MB | 3 archivos |

**Formato de línea:**
```
2025-12-24 14:30:45 | INFO     | app.services.paciente | Paciente creado: paciente_id=42
```

---

## 🛠️ Helpers de Logging Seguros

Ubicación: `app/services/common/log_helpers.py`

### 1. Eventos de Pacientes

```python
from app.services.common.log_helpers import log_paciente_event

# ✅ CORRECTO
log_paciente_event('creado', paciente_id=42)
log_paciente_event('actualizado', paciente_id=42, extra={'obra_social_id': 3})

# ❌ INCORRECTO
logger.info(f"Paciente {paciente.nombre} {paciente.apellido} creado")  # Expone nombre
```

### 2. Eventos de Turnos

```python
from app.services.common.log_helpers import log_turno_event

log_turno_event('creado', turno_id=15, paciente_id=42, fecha='2025-12-25', estado='Confirmado')
log_turno_event('estado_cambiado', turno_id=15, estado='Atendido')
```

### 3. Eventos de Prestaciones

```python
from app.services.common.log_helpers import log_prestacion_event

# Monto solo en creación/eliminación
log_prestacion_event('creada', prestacion_id=30, paciente_id=42, monto=15000.0, practicas_count=3)
log_prestacion_event('actualizada', prestacion_id=30, practicas_count=4)  # Sin monto
```

### 4. Eventos de Seguridad

```python
from app.services.common.log_helpers import log_security_event

# Login exitoso
log_security_event('login', username='florencia', user_id=1, success=True, 
                   ip_address='192.168.1.100', extra='role=DUEÑA')

# Login fallido
log_security_event('login', username='hacker', success=False, 
                   ip_address='192.168.1.200', extra='Invalid credentials')

# Acceso denegado
log_security_event('permission_denied', username='odontologa1', user_id=2,
                   success=False, extra='Attempted access to /finanzas')
```

### 5. Eventos de WhatsApp

```python
from app.services.common.log_helpers import log_whatsapp_event

# Mensaje enviado (teléfono enmascarado automáticamente)
log_whatsapp_event('message_sent', phone_number='+5491112345678', 
                   message_id='wamid.123', success=True)

# Error en envío
log_whatsapp_event('message_failed', phone_number='+5491112345678',
                   success=False, error='Rate limit exceeded')
```

### 6. Eventos de Base de Datos

```python
from app.services.common.log_helpers import log_database_event

log_database_event('backup', extra={'path': 'instance/backups/consultorio_20251224.db'})
log_database_event('restore', extra={'from': 'backup_20251220.db'})
log_database_event('migration', table='pacientes', extra={'added_column': 'obra_social_id'})
```

### 7. Errores con Contexto

```python
from app.services.common.log_helpers import log_error

try:
    # código que puede fallar
    prestacion = crear_prestacion(...)
except Exception as e:
    log_error(e, context='CrearPrestacionService', 
              extra={'paciente_id': 42, 'practicas_count': 3})
    raise
```

---

## 🖥️ Vista de Admin para Logs

**Acceso:** Solo usuarios con rol `ADMIN`

**URL:** `/admin/logs`

### Funcionalidades:

1. **Selector de tipo de log**
   - app (principal)
   - security (seguridad)
   - whatsapp (mensajería)
   - errors (solo errores)

2. **Filtros**
   - Nivel: DEBUG / INFO / WARNING / ERROR
   - Búsqueda de texto libre
   - Cantidad de líneas: 100 / 200 / 500 / 1000 / 5000

3. **Visualización**
   - Colores por nivel (INFO=azul, WARNING=amarillo, ERROR=rojo)
   - Scroll infinito
   - Más recientes primero

4. **Descarga**
   - Botón "Descargar Log" para archivo completo
   - Nombre: `{tipo}_{timestamp}.log`

### Ejemplos de Búsqueda:

- `paciente_id=42` - Todos los eventos del paciente 42
- `ERROR` - Solo líneas con errores
- `login` - Eventos de autenticación
- `whatsapp` - Eventos de WhatsApp
- `prestacion_id=30` - Historia de una prestación específica

---

## 📊 Niveles de Log

| Nivel | Cuándo Usar | Ejemplo |
|-------|-------------|---------|
| `DEBUG` | Desarrollo, debugging detallado | "Query ejecutado: SELECT * FROM..." |
| `INFO` | Eventos normales del sistema | "Turno creado: turno_id=15" |
| `WARNING` | Situaciones anómalas pero no críticas | "Rate limit alcanzado para WhatsApp" |
| `ERROR` | Errores que requieren atención | "Error al enviar mensaje WhatsApp" |

---

## 🚀 Configuración

Variables de entorno (opcional):

```bash
# Nivel de log (default: INFO)
LOG_LEVEL=DEBUG

# Directorio de logs (default: logs/)
LOG_DIR=/var/log/odonto
```

La configuración se aplica automáticamente al iniciar la aplicación.

---

## 🔍 Casos de Uso de Soporte Remoto

### Problema: "No me llegan los mensajes de WhatsApp"

1. Ir a `/admin/logs`
2. Seleccionar tipo: `whatsapp`
3. Buscar: `message_sent` o el teléfono (últimos 4 dígitos)
4. Revisar errores en los intentos de envío
5. Descargar log completo si es necesario

### Problema: "Un usuario no puede iniciar sesión"

1. Ir a `/admin/logs`
2. Seleccionar tipo: `security`
3. Buscar: nombre de usuario
4. Ver intentos de login (SUCCESS/FAILED)
5. Verificar IP, timestamps

### Problema: "La aplicación se cierra inesperadamente"

1. Ir a `/admin/logs`
2. Seleccionar tipo: `errors`
3. Ver últimas excepciones con stack traces
4. Descargar `errors.log` para análisis detallado

### Problema: "No se guardó una prestación"

1. Ir a `/admin/logs`
2. Tipo: `app`
3. Buscar: `prestacion` + timestamp aproximado
4. Ver si hay errores de validación o BD
5. Buscar `prestacion_id` para ver si se creó

---

## 🔒 Seguridad y Auditoría

**Todos los eventos de seguridad son loggeados automáticamente:**

- ✅ Login exitoso/fallido (con IP)
- ✅ Logout
- ✅ Acceso denegado a rutas protegidas
- ✅ Cambios de rol (si se implementa)

**Logs NO son editables** - solo lectura y descarga.

**Retención:** Los logs rotan automáticamente, manteniendo:
- app.log: últimos 100 MB (10 archivos de 10 MB)
- errors.log: últimos 50 MB (5 archivos de 10 MB)
- security.log: últimos 25 MB (5 archivos de 5 MB)
- whatsapp.log: últimos 15 MB (3 archivos de 5 MB)

---

## ✅ Checklist para Desarrolladores

Antes de hacer commit de nuevo código con logging:

- [ ] ¿Usé `log_*_event()` helpers en lugar de `logger.info()` directo?
- [ ] ¿Solo loggeo IDs, nunca nombres o DNI?
- [ ] ¿Los montos solo se loggean en creación/eliminación?
- [ ] ¿Los errores tienen contexto pero sin datos sensibles?
- [ ] ¿Los eventos de seguridad registran IP y resultado?
- [ ] ¿El nivel de log es apropiado (INFO/WARNING/ERROR)?

---

## 📚 Recursos

- **Configuración:** `app/logging_config.py`
- **Helpers:** `app/services/common/log_helpers.py`
- **Vista Admin:** `app/routes/admin.py` → `/admin/logs`
- **Template:** `app/templates/admin/logs.html`

---

## 🆘 Soporte

Si necesitas ayuda con el sistema de logging, contacta al administrador del sistema.

**Recuerda:** Los logs son una herramienta de **diagnóstico técnico**, no de análisis de datos clínicos. Para reportes clínicos, usar las vistas de finanzas y estadísticas.
