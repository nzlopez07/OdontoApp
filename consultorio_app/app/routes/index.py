from datetime import date
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Paciente, Turno, Prestacion
from app.forms import LoginForm
from app.services.usuario import AutenticarUsuarioService
from app.services.common.log_helpers import log_security_event
from . import main_bp


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión con validación WTF."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Los datos ya están validados por WTF
        usuario = AutenticarUsuarioService.execute(form.username.data, form.password.data)
        
        if usuario:
            login_user(usuario, remember=form.remember.data)
            flash(f'Bienvenida, {usuario.nombre_completo}!', 'success')
            
            # Log de login exitoso
            log_security_event(
                event='login',
                username=usuario.username,
                user_id=usuario.id,
                success=True,
                ip_address=request.remote_addr,
                extra=f"rol={usuario.rol}"
            )
            
            # Redirigir a la página que intentaba acceder o al inicio
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            # Log de intento fallido
            log_security_event(
                event='login',
                username=form.username.data,
                success=False,
                ip_address=request.remote_addr,
                extra='Invalid credentials'
            )
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html', form=form)


@main_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario."""
    # Log de logout antes de cerrar sesión
    log_security_event(
        event='logout',
        username=current_user.username,
        user_id=current_user.id,
        success=True,
        ip_address=request.remote_addr
    )
    
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
