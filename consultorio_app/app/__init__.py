import os
from flask import Flask, request, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager
from flasgger import Flasgger
from flask_login import current_user
from app.database import db
from app.database.config import configure_database
from app.database.session import DatabaseSession
from app.logging_config import configure_logging

def create_app():
    app = Flask(__name__)
    
    # Configurar logging ANTES que nada
    configure_logging(app)
    
    # Configurar CORS para permitir peticiones desde Swagger
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configurar secret key para sesiones y CSRF
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurar la base de datos
    configure_database(app)
    
    # Inicializar la base de datos
    db.init_app(app)
    # Registrar singleton para sesiones
    DatabaseSession.get_instance(app)
    
    # Configurar Flask-Login (permite deshabilitarlo para tests con FLASK_LOGIN_DISABLED=1)
    if os.environ.get('FLASK_LOGIN_DISABLED') == '1':
        app.config['LOGIN_DISABLED'] = True

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Ruta para redireccionar si no está autenticado
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))

    @app.before_request
    def proteger_documentacion_swagger():
        # Permitir bypass en entornos de test si FLASK_LOGIN_DISABLED=1
        if app.config.get('LOGIN_DISABLED'):
            return None
        # Proteger /api/docs y /apispec.json con login
        if request.path.startswith('/api/docs') or request.path.startswith('/apispec'):
            if not current_user.is_authenticated:
                return redirect(url_for('main.login', next=request.url))
    
    # Configurar Flasgger para documentación Swagger/OpenAPI
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: rule.rule.startswith('/api/'),
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    flasgger = Flasgger(
        app=app,
        config=swagger_config,
        template={
            "swagger": "2.0",
            "info": {
                "title": "API - Sistema de Gestión Odontológico",
                "description": "Documentación interactiva de endpoints disponibles. Los endpoints /api/* retornan JSON para integración con herramientas externas.",
                "version": "1.0.0",
                "contact": {
                    "name": "Soporte"
                }
            },
            "host": "localhost:5000",
            "basePath": "/",
            "schemes": ["http"],
        }
    )
    
    # Registrar blueprints (rutas)
    from app.routes import main_bp
    from app.routes.webhooks import webhooks_bp
    from app.routes.admin import admin_bp
    from app.routes.finanzas import finanzas_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(finanzas_bp)
    
    return app