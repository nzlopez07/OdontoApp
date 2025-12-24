import os
from flask import Flask

def configure_database(app: Flask):
    """
    Configura la base de datos para la aplicación Flask
    """
    # Configuración de la base de datos
    instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Si estamos en modo TESTING, usar SQLite en memoria para tests rápidos
    if app.config.get('TESTING') or os.environ.get('TESTING') == '1':
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///consultorio.db"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False  # Cambiar a True para ver las consultas SQL
    
    return app
