"""
Rutas exclusivas para el rol ADMIN.
"""

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from functools import wraps
import os
import logging
from datetime import datetime
from app.models import Usuario, Paciente, Turno, Prestacion
from app.database import db
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorador para requerir rol ADMIN."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.tiene_acceso_admin():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal de administración."""
    
    # Estadísticas de BD
    stats = {
        'usuarios': Usuario.query.count(),
        'pacientes': Paciente.query.count(),
        'turnos': Turno.query.count(),
        'prestaciones': Prestacion.query.count(),
    }
    
    # Información de la base de datos
    db_path = db.engine.url.database
    db_info = {
        'ruta': db_path,
        'existe': os.path.exists(db_path) if db_path else False,
        'tamano': None,
        'ultima_modificacion': None
    }
    
    if db_info['existe']:
        db_info['tamano'] = os.path.getsize(db_path)
        db_info['ultima_modificacion'] = datetime.fromtimestamp(
            os.path.getmtime(db_path)
        ).strftime('%Y-%m-%d %H:%M:%S')
    
    # Leer últimas líneas del log
    log_lines = []
    log_file = 'logs/app.log'
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()[-50:]  # Últimas 50 líneas
                log_lines.reverse()  # Más recientes primero
        except Exception as e:
            log_lines = [f"Error leyendo log: {str(e)}"]
    else:
        log_lines = ["Archivo de log no encontrado"]
    
    # Usuarios del sistema
    usuarios = Usuario.query.order_by(Usuario.ultimo_login.desc()).all()
    
    # Información de backups
    backups = []
    backup_dir = 'instance/backups'
    if os.path.exists(backup_dir):
        for filename in sorted(os.listdir(backup_dir), reverse=True)[:10]:
            filepath = os.path.join(backup_dir, filename)
            backups.append({
                'nombre': filename,
                'tamano': os.path.getsize(filepath),
                'fecha': datetime.fromtimestamp(
                    os.path.getmtime(filepath)
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        db_info=db_info,
        log_lines=log_lines,
        usuarios=usuarios,
        backups=backups
    )


@admin_bp.route('/logs')
@login_required
@admin_required
def ver_logs():
    """Ver logs completos del sistema."""
    log_lines = []
    log_file = 'logs/app.log'
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                log_lines.reverse()  # Más recientes primero
        except Exception as e:
            log_lines = [f"Error leyendo log: {str(e)}"]
    else:
        log_lines = ["Archivo de log no encontrado"]
    
    return render_template('admin/logs.html', log_lines=log_lines)
