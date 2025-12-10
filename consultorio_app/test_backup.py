import sys
import os

# Agregar los directorios necesarios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.database.utils import backup_database, list_backups

# Crear la aplicación Flask
app = create_app()

# Trabajar dentro del contexto de la aplicación
with app.app_context():
    print("🔧 Probando funciones de respaldo...")
    
    # Crear un backup
    backup_name = backup_database()
    
    # Listar backups
    backups = list_backups()
    print(f"📋 Backups disponibles: {len(backups)}")
    for backup in backups:
        print(f"   - {backup}")
    
    print("✅ Prueba de respaldo completada")
