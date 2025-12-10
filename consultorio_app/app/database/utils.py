import os
import shutil
from datetime import datetime
from app.database import db
from flask import current_app

def init_database():
    """
    Inicializa la base de datos creando todas las tablas
    """
    with current_app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada correctamente")

def drop_database():
    """
    Elimina todas las tablas de la base de datos
    """
    with current_app.app_context():
        db.drop_all()
        print("🗑️ Base de datos eliminada")

def reset_database():
    """
    Reinicia la base de datos (elimina y crea nuevamente)
    """
    drop_database()
    init_database()
    print("🔄 Base de datos reiniciada")

def get_session():
    """
    Obtiene la sesión actual de la base de datos
    """
    return db.session

def backup_database():
    """
    Crea una copia de respaldo de la base de datos en instance/backups/
    """
    instance_path = os.path.join(current_app.root_path, '..', 'instance')
    backup_path = os.path.join(instance_path, 'backups')
    
    # Crear carpeta de backups si no existe
    os.makedirs(backup_path, exist_ok=True)
    
    # Nombre del archivo de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"consultorio_backup_{timestamp}.db"
    
    # Rutas de origen y destino
    source_db = os.path.join(instance_path, 'consultorio.db')
    backup_db = os.path.join(backup_path, backup_filename)
    
    # Crear el backup
    if os.path.exists(source_db):
        shutil.copy2(source_db, backup_db)
        print(f"💾 Backup creado: {backup_filename}")
        return backup_filename
    else:
        print("⚠️ No se encontró la base de datos para respaldar")
        return None

def restore_database(backup_filename):
    """
    Restaura la base de datos desde un archivo de backup
    """
    instance_path = os.path.join(current_app.root_path, '..', 'instance')
    backup_path = os.path.join(instance_path, 'backups', backup_filename)
    target_db = os.path.join(instance_path, 'consultorio.db')
    
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, target_db)
        print(f"🔄 Base de datos restaurada desde: {backup_filename}")
        return True
    else:
        print(f"⚠️ No se encontró el archivo de backup: {backup_filename}")
        return False

def list_backups():
    """
    Lista todos los archivos de backup disponibles
    """
    instance_path = os.path.join(current_app.root_path, '..', 'instance')
    backup_path = os.path.join(instance_path, 'backups')
    
    if os.path.exists(backup_path):
        backups = [f for f in os.listdir(backup_path) if f.endswith('.db')]
        backups.sort(reverse=True)  # Más recientes primero
        return backups
    else:
        return []
