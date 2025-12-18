from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from app.models import Paciente, Estado
from app.services.turno_service import TurnoService
from . import main_bp


ESTADOS_VALIDOS = ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']


@main_bp.route('/turnos')
def listar_turnos():
    """Lista todos los turnos, opcionalmente filtrados por fecha.
    
    ---
    tags:
      - Turnos
    parameters:
      - name: fecha
        in: query
        type: string
        format: date
        description: Filtrar por fecha específica (YYYY-MM-DD)
      - name: buscar
        in: query
        type: string
        description: Buscar por nombre, apellido o DNI del paciente
    responses:
      200:
        description: Lista de turnos obtenida exitosamente
    """
    fecha_filtro = request.args.get('fecha')
    termino = request.args.get('buscar', '').strip()
    turnos = TurnoService.listar_turnos(fecha_filtro, termino)
    return render_template('turnos/lista.html', turnos=turnos, fecha_filtro=fecha_filtro, termino=termino)


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
            turno = TurnoService.crear_turno({
                'paciente_id': request.form['paciente_id'],
                'fecha': datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
                'hora': datetime.strptime(request.form['hora'], '%H:%M').time(),
                'detalle': request.form.get('detalle'),
                'estado': request.form.get('estado', 'Pendiente'),
            })
            flash('Turno creado exitosamente', 'success')
            return redirect(url_for('main.listar_turnos'))
        except Exception as e:
            flash(f'Error al crear turno: {str(e)}', 'error')

    pacientes = Paciente.query.all()
    estados = Estado.query.all()
    return render_template('turnos/nuevo.html', pacientes=pacientes, estados=estados)


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
