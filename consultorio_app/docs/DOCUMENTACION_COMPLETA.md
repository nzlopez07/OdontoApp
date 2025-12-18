# 📋 DOCUMENTACIÓN COMPLETA - Sistema de Gestión de Consultorio Odontológico

**Versión:** 1.0.0  
**Estado:** Funcional con documentación interactiva  
**Fecha:** Diciembre 2025

---

## 📑 TABLA DE CONTENIDOS

1. [Visión General](#visión-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Modelos de Datos](#modelos-de-datos)
4. [Sistema de Rutas](#sistema-de-rutas)
5. [API JSON con Swagger](#api-json-con-swagger)
6. [Base de Datos](#base-de-datos)
7. [Componentes Clave](#componentes-clave)
8. [Flujos de Negocio](#flujos-de-negocio)
9. [Configuración y Deployment](#configuración-y-deployment)

---

## 🎯 VISIÓN GENERAL

### Propósito
Sistema web para gestionar una clínica odontológica con funcionalidades de:
- Gestión de pacientes
- Programación de turnos/citas
- Registro de prestaciones
- Historial de cambios
- API REST documentada con Swagger/OpenAPI

### Stack Tecnológico
```
Frontend:        Bootstrap 5.3 + Jinja2 Templates
Backend:         Flask 3.1.1 (Python)
ORM:             SQLAlchemy 2.0.41
Base de Datos:   SQLite
API Docs:        Flasgger (Swagger/OpenAPI 2.0)
CORS:            Flask-CORS
Venv:            Python 3.13
```

### Estado Actual
✅ **Funcional:**
- CRUD completo para 3 entidades principales
- Interface web responsiva
- API JSON documentada
- Lógica de validación de turnos vencidos
- Historial de cambios de estado
- Respaldos automáticos

---

## 🏗️ ARQUITECTURA DEL PROYECTO

### Estructura de Directorios

```
ProyectoOdonto/
│
├── consultorio_app/                    # Directorio principal de la app
│   ├── app/                            # Paquete de la aplicación Flask
│   │   ├── __init__.py                # Inicialización y configuración de Flask
│   │   │
│   │   ├── database/                  # Gestión de base de datos
│   │   │   ├── __init__.py            # Instancia de SQLAlchemy: db = SQLAlchemy()
│   │   │   ├── config.py              # Configuración: URI, ECHO, TRACK_MODIFICATIONS
│   │   │   ├── session.py             # DatabaseSession: Singleton para inyección
│   │   │   └── utils.py               # Utilidades: backup, restore, init, drop, reset
│   │   │
│   │   ├── models/                    # Modelos ORM (SQLAlchemy)
│   │   │   ├── __init__.py            # Importación centralizada de modelos
│   │   │   ├── paciente.py            # Modelo Paciente (13 campos)
│   │   │   ├── turno.py               # Modelo Turno (9 campos)
│   │   │   ├── cambioEstado.py        # Modelo CambioEstado (historial)
│   │   │   ├── estado.py              # Modelo Estado (legacy)
│   │   │   ├── localidad.py           # Modelo Localidad (referencia)
│   │   │   ├── obraSocial.py          # Modelo ObraSocial (referencia)
│   │   │   ├── prestacion.py          # Modelo Prestacion (tratamientos)
│   │   │   └── codigo.py              # Modelo Codigo (códigos de operación)
│   │   │
│   │   ├── routes/                    # Rutas organizadas por dominio
│   │   │   ├── __init__.py            # Blueprint main_bp centralizado
│   │   │   ├── index.py               # GET /  (dashboard)
│   │   │   ├── pacientes.py           # CRUD /pacientes
│   │   │   ├── turnos.py              # CRUD /turnos (con validaciones)
│   │   │   ├── prestaciones.py        # CRUD /prestaciones
│   │   │   ├── api.py                 # Endpoints JSON /api/* (Swagger)
│   │   │   └── main.py                # Legacy (vacío, sin usar)
│   │   │
│   │   ├── services/                  # Lógica de negocio (futura)
│   │   │   ├── __init__.py
│   │   │   ├── busqueda_utils.py      # BusquedaUtils para pacientes
│   │   │   ├── turno_service.py       # TurnoService (pendiente)
│   │   │   └── turno_utils.py         # TurnoUtils (pendiente)
│   │   │
│   │   ├── templates/                 # Templates Jinja2
│   │   │   ├── base.html              # Layout principal (navbar, estructura)
│   │   │   ├── index.html             # Dashboard con estadísticas
│   │   │   ├── pacientes/
│   │   │   │   ├── lista.html         # Listado con búsqueda
│   │   │   │   ├── formulario.html    # Create/Edit
│   │   │   │   └── detalle.html       # Vista de paciente + historial
│   │   │   ├── turnos/
│   │   │   │   ├── lista.html         # Listado filtrable
│   │   │   │   └── nuevo.html         # Crear turno
│   │   │   └── prestaciones/
│   │   │       ├── lista.html         # Listado
│   │   │       └── nueva.html         # Crear prestación
│   │   │
│   │   └── __pycache__/               # Cache de Python (ignorar)
│   │
│   ├── instance/                      # Datos específicos de instalación
│   │   ├── consultorio.db            # Base de datos SQLite
│   │   └── backups/                  # Respaldos automáticos
│   │
│   ├── run.py                         # Punto de entrada: python run.py
│   ├── help.py                        # Ayuda interactiva: python help.py
│   ├── quick_start.py                 # Verificación rápida: python quick_start.py
│   ├── test_models.py                 # Pruebas de modelos
│   ├── test_backup.py                 # Pruebas de respaldo
│   ├── init_system.py                 # Inicialización completa
│   ├── test_turno_services.py         # Pruebas de servicios (futuro)
│   └── README.md                      # Documentación básica
│
├── .venv/                             # Virtual environment (Python 3.13)
│   └── Scripts/
│       └── python.exe                 # Python ejecutable
│
└── DOCUMENTACION_COMPLETA.md          # Este archivo
```

### Flujo de Inicialización

```
1. run.py (punto de entrada)
   ↓
2. create_app() en app/__init__.py
   ├─ Configurar SECRET_KEY
   ├─ configure_database(app) → app/database/config.py
   │  └─ Configurar SQLite URI y parámetros
   ├─ db.init_app(app) → Inicializar SQLAlchemy
   ├─ DatabaseSession.get_instance(app) → Singleton para inyección
   ├─ CORS(app) → Habilitar cross-origin requests
   ├─ Flasgger(app) → Swagger en /api/docs
   └─ app.register_blueprint(main_bp) → Registrar todas las rutas
   ↓
3. Flask inicia servidor en 127.0.0.1:5000
   ├─ Base de datos verificada
   ├─ Datos por defecto inicializados (init_default_data)
   └─ Servidor listo para peticiones
```

---

## 💾 MODELOS DE DATOS

### 1. **PACIENTE** (tabla: pacientes)
```python
class Paciente(db.Model):
    __tablename__ = "pacientes"
    
    # Campos identificadores
    id                  → Integer (PK)
    
    # Datos personales
    nombre              → String (requerido)
    apellido            → String (requerido)
    dni                 → String (requerido, único implícito)
    fecha_nac           → Date (requerido)
    telefono            → String (opcional)
    direccion           → String (opcional)
    barrio              → String (opcional)
    
    # Referencias
    localidad_id        → Integer (FK → localidades)
    obra_social_id      → Integer (FK → obras_sociales)
    
    # Datos de afiliación
     nro_afiliado        → String (opcional)
    titular             → String (opcional)
    parentesco          → String (opcional)
    lugar_trabajo       → String (opcional)
    
    # Relaciones
     turnos              → Relationship[Turno] (cascade delete)
     prestaciones        → Relationship[Prestacion]
```

**Métodos:**
- `__str__()` → "Apellido, Nombre (DNI: xxx)"
- `agendar_turno(turno)` → Agregar turno
- `registrar_prestacion(prestacion)` → Agregar prestación

---

### 2. **TURNO** (tabla: turnos)
```python
class Turno(db.Model):
    __tablename__ = "turnos"
    
    # Identificadores
    id                  → Integer (PK)
    
    # Datos del turno
    fecha               → Date (requerido)
    hora                → Time (requerido)
    detalle             → String (opcional)
    estado              → String (Pendiente|Confirmado|Atendido|NoAtendido|Cancelado)
    
    # Referencias
    paciente_id         → Integer (FK → pacientes)
     prestacion_id       → Integer (FK → prestaciones, opcional)
    
    # Relaciones
    paciente            → Relationship[Paciente]
    cambios_estado      → Relationship[CambioEstado] (cascade delete)
     prestacion          → Relationship[Prestacion]
```

**Estados válidos:**
- `Pendiente` → Creado pero no confirmado
- `Confirmado` → Confirmado por el consultorio
- `Atendido` → Ya se realizó la consulta
- `NoAtendido` → Pasó la hora y no se atendió
- `Cancelado` → Cancelado manualmente

**Lógica especial:**
- **Auto-actualización a NoAtendido:**
  - Si `fecha < hoy` → automáticamente NoAtendido
  - Si `fecha == hoy` y `hora < ahora_actual` → automáticamente NoAtendido
  - Se ejecuta en: listar_turnos(), api_listar_turnos(), y endpoint POST /api/turnos/sync/actualizar-vencidos

---

### 3. **CAMBIO_ESTADO** (tabla: cambios_estado)
```python
class CambioEstado(db.Model):
    __tablename__ = "cambios_estado"
    
    # Identificadores
    id                  → Integer (PK)
    
    # Datos del cambio
    estado_anterior     → String (el estado antes del cambio)
    estado_nuevo        → String (el estado después del cambio)
    fecha_cambio        → DateTime (cuándo se cambió)
    motivo              → String (por qué se cambió, opcional)
    
    # Referencias
    turno_id            → Integer (FK → turnos)
    
    # Relaciones
    turno               → Relationship[Turno]
```

**Propósito:** Auditoría y historial completo de cambios en turnos

---

### 4. **ESTADO** (tabla: estados) - LEGACY
```python
class Estado(db.Model):
    __tablename__ = "estados"
    
    id                  → Integer (PK)
    nombre              → String (unique)
```

**Nota:** Este modelo es legacy. Anteriormente se usaba para FK, pero ahora los estados son strings en Turno.CambioEstado para simplificar.

---

### 5. **LOCALIDAD** (tabla: localidades)
```python
class Localidad(db.Model):
    __tablename__ = "localidades"
    
    id                  → Integer (PK)
    nombre              → String
    
    # Relaciones
    pacientes           → Relationship[Paciente]
```

**Datos por defecto (init_default_data):**
- La Plata, Tolosa, Villa Elisa, Gonnet, Ringuelet, Los Hornos

---

### 6. **OBRA_SOCIAL** (tabla: obras_sociales)
```python
class ObraSocial(db.Model):
    __tablename__ = "obras_sociales"
    
    id                  → Integer (PK)
    nombre              → String
    
    # Relaciones
    pacientes           → Relationship[Paciente]
```

**Datos por defecto (init_default_data):**
- OSDE, Medife, Swiss Medical, Galeno, IPAM, Provincia ART, Farmacéutica, SMP

---

### 7. **PRESTACION** (tabla: prestaciones)
```python
class Prestacion(db.Model):
     __tablename__ = "prestaciones"
    
     # Identificadores
     id                  → Integer (PK)
    
     # Datos
     descripcion         → String (requerido)
     monto               → Float (requerido)
     fecha               → DateTime (requerido)
     observaciones       → String (opcional)
    
     # Referencias
     paciente_id         → Integer (FK → pacientes)
     codigo_id           → Integer (FK → codigos, opcional)
    
     # Relaciones
     paciente            → Relationship[Paciente]
     codigo              → Relationship[Codigo]
     turnos              → Relationship[Turno]
```

**Propósito:** Registrar prestaciones realizadas y su costo

---

### 8. **CODIGO** (tabla: codigos)
```python
class Codigo(db.Model):
    __tablename__ = "codigos"
    
    # Identificadores
    id                  → Integer (PK)
    
    # Datos
    numero              → String
    descripcion         → String
```

**Propósito:** Tabla de referencia para códigos de operaciones odontológicas

---

### Diagrama de Relaciones
```
                    ┌─────────────┐
                    │  Localidad  │
                    └──────┬──────┘
                           │1
                           │
                      ╱────╱
                      │
                 ╱────▼────╲
            ╱────┤ Paciente  ├────╲
            │    └───────────┘     │
            │                      │
            │1                    1│
        ╱───▼───╲          ╱───────▼────╲
     │ Turno  │         │ Prestacion  │
        ├────────┤         ├─────────────┤
        │ estado │         │ monto       │
        │ fecha  │1        │ fecha       │
        │ hora   │────────→│ codigo_id   │
        └────┬───┘     0.. └─────────────┘
             │
             │1
        ╱────▼───────────╲
        │ CambioEstado   │
        ├────────────────┤
        │ estado_anterior│
        │ estado_nuevo   │
        │ fecha_cambio   │
        └────────────────┘

ObraSocial
    │1
    │
Paciente ←──── 1
    │1
    ├────→ Turno (1..*)
     └────→ Prestacion (1..*)

Turno
    ├──→ Paciente (*)
    ├──→ CambioEstado (1..*, cascade delete)
     └──→ Prestacion (0..1)
```

---

## 🛣️ SISTEMA DE RUTAS

### Rutas Organizadas por Blueprint

**Blueprint:** `main_bp` (Blueprint centralizado en app/routes/__init__.py)

#### **routes/index.py** - Dashboard
```
GET  /
     ├─ Retorna: template 'index.html'
     ├─ Datos:
     │  ├─ stats: {pacientes: int, turnos: int, turnos_hoy: int, prestaciones: int}
     │  └─ turnos_proximos: List[Turno] (próximos 5 turnos)
     └─ Template variables: stats, turnos_proximos
```

#### **routes/pacientes.py** - CRUD Pacientes
```
GET  /pacientes
     ├─ Query params: ?buscar=término
     ├─ Retorna: template 'pacientes/lista.html'
     └─ Lógica: Busca por nombre, apellido, DNI si se proporciona término

GET  /pacientes/nuevo
     ├─ Retorna: template 'pacientes/formulario.html'
     └─ Variables: obras_sociales, localidades (para dropdowns)

POST /pacientes/nuevo
     ├─ Body: form-data con campos de Paciente
     ├─ Lógica:
     │  ├─ Validar datos
     │  ├─ Crear instancia de Paciente
     │  └─ Guardar en BD
     ├─ Response: redirect('/pacientes') con flash "éxito"
     └─ Error: flash con descripción del error

GET  /pacientes/<id>
     ├─ Path param: id → int
     ├─ Retorna: template 'pacientes/detalle.html'
     ├─ Variables:
     │  ├─ paciente: Paciente object
     │  ├─ edad: int (calculada)
     │  ├─ turnos: List[Turno] (ordenados por fecha DESC)
     │  ├─ operaciones: List[Operacion] (ordenados por fecha DESC)
     │  └─ estadisticas: {total_turnos, total_operaciones}
     └─ Error: 404 si no existe

GET  /pacientes/<id>/editar
     ├─ Path param: id → int
     ├─ Retorna: template 'pacientes/formulario.html' (prellenado)
     └─ Variables: paciente, obras_sociales, localidades

POST /pacientes/<id>/editar
     ├─ Path param: id → int
     ├─ Body: form-data con campos actualizados
     ├─ Lógica:
     │  ├─ Obtener paciente
     │  ├─ Actualizar campos
     │  └─ Guardar en BD
     ├─ Response: redirect('/pacientes/<id>') con flash
     └─ Error: flash con descripción
```

#### **routes/turnos.py** - CRUD Turnos con Validaciones
```
GET  /turnos
     ├─ Query params: ?fecha=YYYY-MM-DD&buscar=término&estado=Pendiente|Confirmado|Atendido|NoAtendido|Cancelado
     ├─ Lógica especial:
     │  └─ SIEMPRE ejecuta: _actualizar_no_atendidos(session)
     │     └─ Marca como NoAtendido si fecha < hoy O (fecha == hoy Y hora < ahora)
     ├─ Retorna: template 'turnos/lista.html'
     └─ Variables: turnos (filtrados), fecha_filtro, termino

GET  /turnos/nuevo
     ├─ Retorna: template 'turnos/nuevo.html'
     └─ Variables: pacientes, estados

POST /turnos/nuevo
     ├─ Body: form-data {paciente_id, fecha, hora, detalle, estado}
     ├─ Lógica:
     │  ├─ Crear Turno
     │  ├─ estado defecto: 'Pendiente'
     │  └─ Guardar
     ├─ Response: redirect('/turnos') con flash
     └─ Error: flash

POST /turnos/<id>/estado
     ├─ Path param: id → int
     ├─ Body: form-data {estado: string}
     ├─ Validaciones:
     │  ├─ estado ∈ ESTADOS_VALIDOS
     │  ├─ No se puede cancelar NoAtendido
     │  └─ Si fecha < hoy: FUERZA estado = NoAtendido
     ├─ Lógica:
     │  ├─ Obtener turno
     │  ├─ Registrar cambio en CambioEstado
     │  │  └─ {turno_id, estado_anterior, estado_nuevo, fecha_cambio, motivo}
     │  └─ Actualizar turno.estado
     ├─ Response: redirect('/turnos') con flash
     └─ Error: flash

POST /turnos/<id>/eliminar
     ├─ Path param: id → int
     ├─ Validaciones:
     │  └─ Turno.estado == 'Pendiente' (única regla)
     ├─ Lógica:
     │  ├─ Obtener turno
     │  ├─ Eliminar turnos_relacionados.cambios_estado (cascade)
     │  └─ Eliminar turno
     ├─ Response: redirect('/turnos') con flash
     └─ Error: flash si no es Pendiente
```

#### **routes/prestaciones.py** - CRUD Prestaciones
```
GET  /prestaciones
     ├─ Retorna: template 'prestaciones/lista.html'
     └─ Variables: prestaciones (ordenadas por fecha DESC)

GET  /prestaciones/nueva
     ├─ Retorna: template 'prestaciones/nueva.html'
     └─ Variables: pacientes, codigos

POST /prestaciones/nueva
     ├─ Body: form-data {paciente_id, descripcion, monto, codigo_id, observaciones}
     ├─ Lógica:
     │  ├─ Crear Prestacion
     │  ├─ fecha = datetime.now()
     │  └─ Guardar
     ├─ Response: redirect('/prestaciones') con flash
     └─ Error: flash
```

#### **routes/api.py** - API JSON (Swagger documentada)
```
GET  /api/pacientes
     ├─ Query params: ?buscar=término
     ├─ Retorna: JSON {pacientes: [{id, nombre, apellido, dni, fecha_nac, ...}]}
     └─ Swagger: tags=Pacientes

GET  /api/pacientes/<id>
     ├─ Retorna: JSON {id, nombre, apellido, dni, edad, telefono, turnos_cantidad, prestaciones_cantidad}
     └─ Swagger: tags=Pacientes

GET  /api/turnos
     ├─ Query params: ?fecha=YYYY-MM-DD&buscar=término&estado=...
     ├─ Lógica: EJECUTA _actualizar_no_atendidos(session) SIEMPRE
     ├─ Retorna: JSON {turnos: [{id, fecha, hora, estado, paciente_nombre, ...}], cantidad}
     └─ Swagger: tags=Turnos

GET  /api/turnos/<id>
     ├─ Lógica: EJECUTA _actualizar_no_atendidos(session)
     ├─ Retorna: JSON {id, fecha, hora, estado, detalle, paciente, cambios_estado}
     └─ Swagger: tags=Turnos

POST /api/turnos/sync/actualizar-vencidos
     ├─ Lógica: Fuerza actualización manual de turnos vencidos
     ├─ Retorna: JSON {mensaje, cantidad}
     └─ Swagger: tags=Turnos

GET  /api/prestaciones
     ├─ Query params: ?paciente_id=int
     ├─ Retorna: JSON {prestaciones: [{id, descripcion, monto, fecha, paciente_nombre, ...}], cantidad}
     └─ Swagger: tags=Prestaciones

GET  /api/prestaciones/<id>
     ├─ Retorna: JSON {id, descripcion, monto, fecha, observaciones, paciente}
     └─ Swagger: tags=Prestaciones

GET  /api/estados
     ├─ Retorna: JSON {estados: ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']}
     └─ Swagger: tags=Configuración

GET  /api/docs (SWAGGER UI)
     └─ Interfaz interactiva donde puedes ejecutar requests a todos los /api/* endpoints

GET  /apispec.json
     └─ Especificación OpenAPI 2.0 en JSON (utilizada por Swagger UI)
```

---

## 🔌 API JSON CON SWAGGER

### Activación
- **Librería:** Flasgger 0.9.7.1
- **Configuración:** En app/__init__.py
- **Punto de acceso:** http://127.0.0.1:5000/api/docs
- **Especificación:** http://127.0.0.1:5000/apispec.json

### Características
✅ Interfaz web interactiva  
✅ Documentación automática de todos los endpoints  
✅ Prueba endpoints directamente desde el navegador  
✅ Parámetros documentados con tipos  
✅ Respuestas de ejemplo  
✅ CORS habilitado (Flask-CORS)

### Flujo de Swagger
```
1. Usuario abre http://127.0.0.1:5000/api/docs en navegador
   ↓
2. Swagger UI carga y solicita /apispec.json
   ↓
3. Flasgger analiza docstrings YAML en routes/api.py
   ↓
4. Genera spec OpenAPI 2.0 y lo retorna
   ↓
5. Swagger UI renderiza interfaz interactiva
   ├─ Agrupa endpoints por tags
   ├─ Muestra parámetros, tipos, descripciones
   ├─ Permite click en "Execute" para hacer requests
   └─ Muestra respuestas en tiempo real
   ↓
6. Petición CORS a /api/* endpoint
   ├─ CORS headers permiten request desde navegador
   ├─ Endpoint procesa y retorna JSON
   └─ Swagger muestra response en interfaz
```

### Documentación en Código (Docstrings YAML)
Cada endpoint API tiene formato:
```python
@main_bp.route('/api/turnos')
def api_listar_turnos():
    """Get all appointments
    ---
    tags:
      - Turnos
    parameters:
      - name: fecha
        in: query
        type: string
        format: date
      - name: buscar
        in: query
        type: string
    responses:
      200:
        description: List of appointments
    """
    # Implementación...
```

---

## 💾 BASE DE DATOS

### Configuración
```python
# Archivo: app/database/config.py
SQLALCHEMY_DATABASE_URI = "sqlite:///consultorio.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # Cambiar a True para ver SQL queries
```

### Ubicación
- **Archivo:** `instance/consultorio.db`
- **Tipo:** SQLite (archivo)
- **Respaldos:** `instance/backups/consultorio_backup_TIMESTAMP.db`

### Utilidades de BD (app/database/utils.py)
```python
init_database()           # Crea todas las tablas
drop_database()           # Elimina todas las tablas
reset_database()          # drop + init
get_session()             # Obtiene sesión actual
backup_database()         # Crea respaldo automático
restore_database(name)    # Restaura desde respaldo
list_backups()            # Lista respaldos disponibles
```

### Singleton DatabaseSession
```python
# Patrón Singleton para inyección de sesiones
class DatabaseSession:
    _instance = None
    
    @staticmethod
    def get_instance(app=None):
        if DatabaseSession._instance is None:
            DatabaseSession._instance = DatabaseSession(app)
        return DatabaseSession._instance
    
    @property
    def session(self):
        return db.session
```

**Propósito:** Centralizar el acceso a sesiones y permitir inyección consistente

---

## 🔧 COMPONENTES CLAVE

### 1. **DatabaseSession (app/database/session.py)**
- Patrón Singleton
- Evita doble inicialización de db.init_app()
- Proporciona acceso centralizado a sesiones
- Inyectable en rutas

### 2. **BusquedaUtils (app/services/busqueda_utils.py)**
- `buscar_pacientes_simple(termino)` → busca por nombre, apellido, DNI
- Utiliza ILIKE para búsqueda case-insensitive

### 3. **Validaciones de Turnos (app/routes/turnos.py)**
- `_actualizar_no_atendidos(session)` → marca turnos vencidos
- Verifica fecha < hoy O (fecha == hoy Y hora < ahora_actual)
- Se ejecuta antes de listar/consultar turnos

### 4. **Flash Messages**
- `flash('mensaje', 'category')` para feedback al usuario
- Categorías: 'success', 'error', 'warning', 'info'
- Renderizadas en base.html

### 5. **Error Handling**
- `get_or_404(id)` → retorna 404 si no existe
- Try/catch en POST para rollback de BD en caso de error
- Flash de error en interfaz

---

## 📊 FLUJOS DE NEGOCIO

### Flujo 1: Crear Paciente
```
1. Usuario abre /pacientes/nuevo
2. GET /pacientes/nuevo
   ├─ Obtener obras_sociales y localidades
   └─ Renderizar formulario
3. Usuario completa formulario y envía
4. POST /pacientes/nuevo
   ├─ Validar datos en formulario HTML
   ├─ Crear instancia Paciente
   ├─ Agregar a session y commit
   ├─ Flash "Paciente creado exitosamente"
   └─ Redirect a /pacientes/lista
5. Usuario ve nuevo paciente en lista
```

### Flujo 2: Crear Turno
```
1. Usuario abre /turnos/nuevo
2. GET /turnos/nuevo
   ├─ Obtener lista de pacientes
   ├─ Obtener lista de estados
   └─ Renderizar formulario
3. Usuario selecciona paciente, fecha, hora, estado
4. POST /turnos/nuevo
   ├─ Crear Turno(paciente_id, fecha, hora, detalle, estado='Pendiente')
   ├─ Guardar en BD
   ├─ Flash "Turno creado exitosamente"
   └─ Redirect a /turnos
5. Turno visible en listado
```

### Flujo 3: Cambiar Estado de Turno
```
1. Usuario en /turnos ve botones de acciones
2. Usuario hace click en "Cambiar Estado"
3. Usuario selecciona nuevo estado (ej: Atendido)
4. POST /turnos/<id>/estado con estado=Atendido
   ├─ Obtener turno actual
   ├─ Guardar estado_anterior = turno.estado (ej: Pendiente)
   ├─ Crear CambioEstado(turno_id, estado_anterior='Pendiente', estado_nuevo='Atendido', ...)
   ├─ Actualizar turno.estado = 'Atendido'
   ├─ Commit a BD
   ├─ Flash "Estado actualizado"
   └─ Redirect a /turnos
5. Turno ahora muestra nuevo estado
6. Historial de Cambio disponible en /pacientes/<id>
```

### Flujo 4: Auto-marcar Turnos Vencidos
```
Triggers (ejecuta _actualizar_no_atendidos):
├─ GET /turnos
├─ GET /api/turnos
├─ GET /api/turnos/<id>
└─ POST /api/turnos/sync/actualizar-vencidos (manual)

Lógica:
1. Iterar todos los turnos NO en estado [Atendido, NoAtendido, Cancelado]
2. Para cada turno:
   ├─ Si fecha < hoy → turno.estado = 'NoAtendido'
   └─ Si fecha == hoy Y hora < ahora_actual → turno.estado = 'NoAtendido'
3. Si hubo cambios, commit a BD
```

### Flujo 5: Consultar API (Swagger)
```
1. Usuario abre http://127.0.0.1:5000/api/docs
2. Swagger UI carga (solicita /apispec.json)
3. Flasgger procesa docstrings YAML de routes/api.py
4. Swagger renderiza interfaz con todos los endpoints
5. Usuario selecciona endpoint (ej: GET /api/pacientes)
6. Usuario hace click en "Execute"
7. Swagger hace petición CORS a /api/pacientes
8. Servidor ejecuta _actualizar_no_atendidos() si es turno
9. Retorna JSON
10. Swagger muestra respuesta en pantalla
```

---

## 🚀 CONFIGURACIÓN Y DEPLOYMENT

### Instalación Local
```bash
# 1. Clonar o descargar proyecto
cd ProyectoOdonto/consultorio_app

# 2. Crear virtual environment con Python 3.13
python -m venv .venv

# 3. Activar venv (Windows)
.venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar servidor
python run.py

# 6. Acceder en navegador
# - Aplicación: http://127.0.0.1:5000
# - Swagger API: http://127.0.0.1:5000/api/docs
```

### Dependencias (requirements.txt)
```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.41
Flasgger==0.9.7.1
Flask-CORS==6.0.1
python-dateutil==2.8.2
```

### Estructura de Carpetas Importante
```
instance/                    # Carpeta para datos locales
├── consultorio.db          # Base de datos (GENERADA)
└── backups/                # Respaldos (GENERADOS)

.venv/                       # Virtual environment (GENERADO)
```

### Variables de Entorno (opcionales)
```bash
# .env (crear en raíz del proyecto)
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_RESET_DB=1  # Resetear BD en startup (solo desarrollo)
```

### Scripts de Utilidad
```bash
python run.py                 # Ejecutar servidor
python help.py               # Ver ayuda interactiva
python quick_start.py         # Verificación rápida
python test_models.py         # Pruebas de modelos
python test_backup.py         # Pruebas de respaldo
python init_system.py         # Inicialización completa
```

### Estado de Deployment
❌ **No listo para producción**
- Falta autenticación/autorización
- Falta validación de entrada robusta
- Falta HTTPS
- Base de datos sin respaldos automáticos configurados
- Sin logs centralizados
- Sin monitoreo

---

## 📝 RESUMEN EJECUTIVO

### Lo que EXISTE (Implementado)
✅ Base de datos con 8 modelos relacionados  
✅ CRUD completo para Pacientes, Turnos, Operaciones  
✅ Interface web con Bootstrap 5.3  
✅ API REST documentada con Swagger/OpenAPI  
✅ Validación automática de turnos vencidos  
✅ Historial de cambios de estado (auditoría)  
✅ Sistema de respaldos  
✅ CORS habilitado  
✅ Patrón Singleton para inyección  
✅ Búsqueda de pacientes  

### Lo que FALTA (Necesario para Producción)
❌ Autenticación (login/logout)  
❌ Autorización (roles/permisos)  
❌ Validación de entrada en formularios (Frontend + Backend)  
❌ Tests unitarios/integración  
❌ Logging detallado  
❌ Manejo de errores robusto  
❌ HTTPS/SSL  
❌ Scheduler automático (background tasks)  
❌ Documentación de API (aunque existe)  
❌ Optimización de queries  

### Stack Completo
```
Cliente:   Bootstrap 5.3 + Jinja2 + HTML5 + CSS3
Servidor:  Flask 3.1.1 + Python 3.13
ORM:       SQLAlchemy 2.0.41
BD:        SQLite
API Docs:  Flasgger + Swagger UI
Deploy:    (No configurado)
```

---

## 🎓 Conclusión para Aprendizaje

Este proyecto demuestra:

1. **Arquitectura moderada:** Patrón MVC con Blueprints
2. **ORM bien estructurado:** SQLAlchemy con relaciones
3. **API moderna:** Documentada con Swagger/OpenAPI
4. **Validaciones:** Auto-actualización de estados
5. **Auditoría:** Tabla de historial (CambioEstado)

**Próximos pasos educativos:**
1. Agregar autenticación (Flask-Login)
2. Agregar autorización (Flask-Principal)
3. Validaciones robustas (Flask-WTF)
4. Tests (pytest)
5. Logging (logging module)
6. Background tasks (APScheduler)
7. Deployment (gunicorn + nginx + Docker)

