# Sistema de Gestión de Consultorio Odontológico

## 📁 Estructura del Proyecto

```
consultorio_app/
├── app/
│   ├── __init__.py              # Configuración principal de Flask
│   ├── database/                # Gestión de base de datos
│   │   ├── __init__.py         # Instancia de SQLAlchemy
│   │   ├── config.py           # Configuración de BD
│   │   └── utils.py            # Utilidades y backups
│   ├── models/                  # Modelos de datos
│   │   ├── __init__.py         # Importación de todos los modelos
│   │   ├── paciente.py         # Modelo Paciente
│   │   ├── turno.py            # Modelo Turno
│   │   ├── estado.py           # Modelo Estado
│   │   ├── cambioEstado.py     # Modelo CambioEstado
│   │   ├── localidad.py        # Modelo Localidad
│   │   ├── obraSocial.py       # Modelo ObraSocial
│   │   ├── operacion.py        # Modelo Operacion
│   │   └── codigo.py           # Modelo Codigo
│   ├── routes/                  # Rutas de la aplicación
│   └── services/               # Lógica de negocio
├── instance/                   # Datos específicos de la instancia
│   ├── consultorio.db         # Base de datos SQLite
│   └── backups/               # Respaldos automáticos
├── database/                  # Configuración SQLAlchemy puro (legacy)
├── run.py                     # Punto de entrada de la aplicación
├── test_flask_db.py          # Pruebas de base de datos
└── .gitignore                # Archivos excluidos del control de versiones
```

## 🗄️ Carpeta Instance

La carpeta `instance/` es especial en Flask:

- **Propósito**: Almacena datos específicos de cada instalación
- **Contenido**: Base de datos, archivos de configuración local, logs
- **Control de versiones**: Excluida del repositorio (.gitignore)
- **Backups**: Los respaldos se guardan en `instance/backups/`

### Funciones de respaldo disponibles:

```python
from app.database.utils import backup_database, restore_database, list_backups

# Crear respaldo
backup_database()

# Listar respaldos
backups = list_backups()

# Restaurar desde respaldo
restore_database('consultorio_backup_20250721_120000.db')
```

## 🚀 Scripts de Inicialización

### 🔧 `init_system.py` - Inicialización Completa
Script principal para configurar el sistema desde cero:
- Crea y configura la base de datos
- Puebla con datos maestros (estados, localidades, obras sociales, códigos)
- Crea pacientes, turnos y operaciones de ejemplo
- Prueba todas las relaciones entre modelos
- Verifica el sistema de respaldos
- Genera reporte estadístico completo

```bash
python init_system.py
```

### ⚡ `quick_start.py` - Verificación Rápida
Script para uso diario que verifica el estado del sistema:
- Comprueba la conectividad de la base de datos
- Muestra estadísticas básicas
- Crea backup automático
- Confirma que todo funciona correctamente

```bash
python quick_start.py
```

### 🧪 `test_flask_db.py` - Pruebas de Base de Datos
Script de pruebas específicas para validar modelos y relaciones:

```bash
python test_flask_db.py
```

### 💾 `test_backup.py` - Pruebas de Respaldo
Script para probar el sistema de respaldos:

```bash
python test_backup.py
```

## 🚀 Uso

```bash
# Ejecutar la aplicación
python run.py

# Ejecutar pruebas
python test_flask_db.py
```

## 📊 Modelos de Datos

- **Paciente**: Información personal y de contacto
- **Turno**: Citas programadas
- **Estado**: Estados de los turnos (Pendiente, Confirmado, etc.)
- **CambioEstado**: Historial de cambios de estado
- **Operacion**: Tratamientos realizados
- **Codigo**: Códigos de operaciones
- **Localidad**: Ubicaciones geográficas
- **ObraSocial**: Obras sociales
