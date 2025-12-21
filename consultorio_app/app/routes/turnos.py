from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from app.models import Paciente, Estado, Turno, CambioEstado
from app.services.turno_service import TurnoService
from app.services.paciente_service import PacienteService
from . import main_bp


ESTADOS_VALIDOS = ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']


@main_bp.route('/turnos')
def listar_turnos():
    """Muestra la agenda de turnos en vista semanal.
    
    Parámetros opcionales:
    - fecha_inicio: primera fecha de la semana (YYYY-MM-DD). Si no se proporciona, usa la semana actual
    
    Retorna vista de agenda con semana completa (Lunes a Sábado) con turnos organizados por hora
    """
    fecha_inicio_str = request.args.get('fecha_inicio')
    
    # Obtener estructura de agenda para la semana
    datos_agenda = TurnoService.obtener_semana_agenda(fecha_inicio_str)
    
    return render_template('turnos/agenda.html', **datos_agenda)


@main_bp.route('/pacientes/<int:paciente_id>/turnos')
def listar_turnos_paciente(paciente_id: int):
    paciente = PacienteService.obtener_paciente(paciente_id)
    if not paciente:
        flash('Paciente no encontrado', 'error')
        return redirect(url_for('main.listar_pacientes'))

    pagina = request.args.get('pagina', 1, type=int)
    datos_paginacion = TurnoService.listar_turnos_paciente_pagina(paciente_id, pagina=pagina, por_pagina=10)
    
    return render_template(
        'turnos/paciente_lista.html',
        paciente=paciente,
        turnos=datos_paginacion['items'],
        pagina_actual=datos_paginacion['pagina_actual'],
        total_paginas=datos_paginacion['total_paginas'],
        total=datos_paginacion['total'],
    )


@main_bp.route('/turnos/nuevo', methods=['GET', 'POST'])
def nuevo_turno():
    """Crear un nuevo turno.
    
    ---
    tags:
      - Turnos
    parameters:
      - name: paciente_id
        in: form
        type: integer
        required: true
        description: ID del paciente
      - name: fecha
        in: form
        type: string
        format: date
        required: true
        description: Fecha del turno (YYYY-MM-DD)
      - name: hora
        in: form
        type: string
        required: true
        description: Hora del turno (HH:MM)
      - name: detalle
        in: form
        type: string
        description: Detalles del turno
      - name: operacion_id
        in: form
        type: integer
        description: ID de la operación
    responses:
      200:
        description: Formulario para crear turno (GET) o turno creado (POST)
      302:
        description: Redirección después de crear turno exitosamente
    """
    if request.method == 'POST':
        try:
            duracion_form = request.form.get('duracion')
            horas_str = request.form.get('duracion_horas')
            minutos_str = request.form.get('duracion_minutos')
            duracion_minutos = None

            if horas_str is not None or minutos_str is not None:
                try:
                    h = int(horas_str or 0)
                    m = int(minutos_str or 0)
                    duracion_minutos = max(0, h * 60 + m)
                except ValueError:
                    duracion_minutos = None

            if duracion_minutos is None:
                duracion_minutos = int(duracion_form) if duracion_form is not None else 30

            turno = TurnoService.crear_turno({
                'paciente_id': request.form['paciente_id'],
                'fecha': datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
                'hora': datetime.strptime(request.form['hora'], '%H:%M').time(),
                'duracion': duracion_minutos,
                'detalle': request.form.get('detalle'),
                'estado': request.form.get('estado', 'Pendiente'),
            })
            flash('Turno creado exitosamente', 'success')
            paciente_id = request.form.get('paciente_id')
            if paciente_id:
                return redirect(url_for('main.ver_paciente', id=paciente_id))
            return redirect(url_for('main.listar_turnos'))
        except ValueError as e:
            # Errores de validación del servicio
            flash(f'No se pudo crear el turno: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error inesperado al crear turno: {str(e)}', 'error')

    pacientes = Paciente.query.all()
    estados = Estado.query.all()
    return render_template('turnos/nuevo.html', pacientes=pacientes, estados=estados)


@main_bp.route('/turnos/<int:turno_id>')
def ver_turno(turno_id: int):
    """Ver detalles de un turno específico."""
    turno = Turno.query.get(turno_id)
    if not turno:
        flash('Turno no encontrado', 'error')
        return redirect(url_for('main.listar_turnos'))
    
    cambios_estado = CambioEstado.query.filter_by(turno_id=turno_id).order_by(
        CambioEstado.fecha_cambio.desc()
    ).all()
    
    # Obtener estados permitidos para el estado actual
    estado_actual = turno.estado or 'Pendiente'
    estados_permitidos = TurnoService.TRANSICIONES_VALIDAS.get(estado_actual, [])
    
    return render_template(
        'turnos/ver.html',
        turno=turno,
        cambios_estado=cambios_estado,
        estados_permitidos=estados_permitidos
    )


@main_bp.route('/turnos/<int:turno_id>/estado', methods=['POST'])
def cambiar_estado_turno(turno_id: int):
    """Cambiar el estado de un turno con reglas de negocio básicas.
    
    ---
    tags:
      - Turnos
    parameters:
      - name: turno_id
        in: path
        type: integer
        required: true
        description: ID del turno
      - name: estado
        in: form
        type: string
        required: true
        enum: ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']
        description: Nuevo estado del turno
    responses:
      302:
        description: Redirección después de cambiar el estado
      404:
        description: Turno no encontrado
      400:
        description: Estado inválido
    """
    nuevo_estado = request.form.get('estado')

    if nuevo_estado not in ESTADOS_VALIDOS:
        flash('Estado inválido', 'error')
        return redirect(url_for('main.listar_turnos'))

    turno, error = TurnoService.cambiar_estado(turno_id, nuevo_estado)
    if error:
      flash(error, 'error')
    else:
      flash('Estado actualizado', 'success')

    return redirect(url_for('main.listar_turnos'))


@main_bp.route('/turnos/<int:turno_id>/eliminar', methods=['POST'])
def eliminar_turno(turno_id: int):
    """Eliminar un turno. Solo se pueden eliminar turnos Pendientes.
    
    ---
    tags:
      - Turnos
    parameters:
      - name: turno_id
        in: path
        type: integer
        required: true
        description: ID del turno a eliminar
    responses:
      302:
        description: Redirección después de eliminar el turno
      404:
        description: Turno no encontrado
      400:
        description: No se puede eliminar un turno que no está Pendiente
    """
    turno, error = TurnoService.eliminar_turno(turno_id)
    if error:
      flash(error, 'error')
    else:
      flash('Turno eliminado exitosamente', 'success')
    
    return redirect(url_for('main.listar_turnos'))
