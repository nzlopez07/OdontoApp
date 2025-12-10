from flask import Flask
from app.database import db
from app.database.config import configure_database

def create_app():
    app = Flask(__name__)
    
    # Configurar la base de datos
    configure_database(app)
    
    # Inicializar la base de datos
    db.init_app(app)
    
    # Registrar blueprints (rutas)
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app