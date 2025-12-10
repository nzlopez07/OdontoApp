#!/usr/bin/env python3
"""
Script de inicio rápido del Sistema de Gestión de Consultorio Odontológico
Uso diario para verificar que todo funcione correctamente.
"""

import sys
import os

# Agregar los directorios necesarios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.database import db
from app.database.utils import backup_database
from app.models import (
    Paciente, Turno, Estado, CambioEstado, 
    Localidad, ObraSocial, Operacion, Codigo
)

def quick_check():
    """Verificación rápida del sistema"""
    print("🏥 Sistema de Gestión de Consultorio Odontológico")
    print("=" * 50)
    
    # Crear aplicación
    app = create_app()
    
    with app.app_context():
        # Verificar base de datos
        try:
            db.create_all()  # Asegurar que las tablas existan
            
            # Contar registros
            stats = {
                "Pacientes": Paciente.query.count(),
                "Turnos": Turno.query.count(), 
                "Estados": Estado.query.count(),
                "Operaciones": Operacion.query.count(),
            }
            
            print("📊 Estado actual:")
            for tabla, cantidad in stats.items():
                print(f"   {tabla}: {cantidad} registros")
            
            # Crear backup automático
            backup_name = backup_database()
            if backup_name:
                print(f"💾 Backup automático: {backup_name}")
            
            print("✅ Sistema funcionando correctamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = quick_check()
    if not success:
        sys.exit(1)
