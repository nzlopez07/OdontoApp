#!/usr/bin/env python3
"""
Punto de entrada principal para el Sistema de Gestión de Consultorio Odontológico
Ejecuta el servidor web Flask para la aplicación.
"""

import os
import sys
from app import create_app
from app.database import db
from app.models import *  # Importar todos los modelos para que SQLAlchemy los reconozca

def main():
    app = create_app()

    with app.app_context():
        db.create_all()
        print("✅ Base de datos verificada")
    
    # Configuración del servidor
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Iniciando servidor en http://{host}:{port}")
    print("📋 Para ver ayuda: python help.py")
    print("⚡ Para verificación rápida: python quick_start.py")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()