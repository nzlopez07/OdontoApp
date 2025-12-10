#!/usr/bin/env python3
"""
Script de ayuda para el Sistema de Gestión de Consultorio Odontológico
Muestra todos los comandos y scripts disponibles.
"""

def show_help():
    """Muestra la ayuda del sistema"""
    
    help_text = """
🏥 SISTEMA DE GESTIÓN DE CONSULTORIO ODONTOLÓGICO
===============================================

📋 SCRIPTS DISPONIBLES:
-----------------------

🔧 init_system.py
   └─ Inicialización completa del sistema
   └─ Crea base de datos y datos de ejemplo
   └─ Uso: python init_system.py

⚡ quick_start.py  
   └─ Verificación rápida del sistema
   └─ Chequeo diario de estado
   └─ Uso: python quick_start.py

🧪 test_models.py
   └─ Pruebas automatizadas de modelos y BD
   └─ Validación de relaciones y restricciones
   └─ Uso: python test_models.py

💾 test_backup.py
   └─ Pruebas del sistema de respaldos
   └─ Gestión de backups
   └─ Uso: python test_backup.py

🚀 run.py
   └─ Punto de entrada de la aplicación Flask
   └─ Servidor web de desarrollo
   └─ Uso: python run.py

❓ help.py
   └─ Este archivo de ayuda
   └─ Uso: python help.py

📁 ESTRUCTURA DE ARCHIVOS:
--------------------------

app/
├── __init__.py           # Configuración Flask
├── database/             # Gestión de BD
│   ├── __init__.py      # SQLAlchemy instance  
│   ├── config.py        # Configuración de BD
│   └── utils.py         # Utilidades y backups
└── models/              # Modelos de datos
    ├── __init__.py      # Importación de modelos
    ├── paciente.py      # Modelo Paciente
    ├── turno.py         # Modelo Turno
    ├── estado.py        # Modelo Estado
    ├── cambioEstado.py  # Modelo CambioEstado
    ├── localidad.py     # Modelo Localidad
    ├── obraSocial.py    # Modelo ObraSocial
    ├── operacion.py     # Modelo Operacion
    └── codigo.py        # Modelo Codigo

instance/
├── consultorio.db       # Base de datos principal
└── backups/             # Respaldos automáticos

🛠️  COMANDOS ÚTILES:
--------------------

📊 Ver estado del sistema:
   python quick_start.py

🔄 Reiniciar sistema completo:
   python init_system.py

💾 Crear respaldo manual:
   python test_backup.py

🧪 Probar modelos y BD:
   python test_models.py

🌐 Iniciar servidor web:
   python run.py

📖 DOCUMENTACIÓN:
-----------------
Ver README.md para documentación completa.

🆘 SOPORTE:
-----------
Si encuentras problemas:
1. Ejecuta quick_start.py para verificar el estado
2. Revisa los logs de error
3. Considera ejecutar init_system.py para reiniciar

===============================================
"""
    
    print(help_text)

if __name__ == "__main__":
    show_help()
