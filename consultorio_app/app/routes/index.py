from datetime import date
from flask import render_template
from app.models import Paciente, Turno, Prestacion
from . import main_bp


@main_bp.route('/')
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
