from datetime import date
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Paciente, Turno, Prestacion
from app.services.usuario import AutenticarUsuarioService
from . import main_bp


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        usuario = AutenticarUsuarioService.execute(username, password)
        
        if usuario:
            login_user(usuario, remember=remember)
            flash(f'Bienvenida, {usuario.nombre_completo}!', 'success')
            
            # Redirigir a la página que intentaba acceder o al inicio
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario."""
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('main.login'))


@main_bp.route('/')
@login_required
def index():
    """Página principal con estadísticas y próximos turnos.
    
    ---
    tags:
      - Inicio
    responses:
      200:
        description: Dashboard con estadísticas del sistema
    """
    stats = {
        'pacientes': Paciente.query.count(),
        'turnos': Turno.query.count(),
        'turnos_hoy': Turno.query.filter_by(fecha=date.today()).count(),
        'prestaciones': Prestacion.query.count(),
    }

    turnos_proximos = (
        Turno.query
        .filter(Turno.fecha >= date.today())
        .order_by(Turno.fecha, Turno.hora)
        .limit(5)
        .all()
    )

    return render_template('index.html', stats=stats, turnos_proximos=turnos_proximos)
