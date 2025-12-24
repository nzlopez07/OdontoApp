from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Paciente, Estado, Turno, CambioEstado
from app.forms import TurnoForm
from app.services.turno import (
    AgendarTurnoService,
    CambiarEstadoTurnoService,
    ObtenerAgendaService,
    ListarTurnosService,
    EliminarTurnoService,
    EditarTurnoService,
)
from app.services.paciente import BuscarPacientesService
from app.services.common import (
    TurnoNoEncontradoError,
    TransicionEstadoInvalidaError,
    EstadoTurnoInvalidoError,
    TurnoSolapamientoError,
    TurnoFechaInvalidaError,
    PacienteNoEncontradoError,
    EstadoFinalError,
)
from . import main_bp


ESTADOS_VALIDOS = ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']


@main_bp.route('/turnos')
@login_required
def listar_turnos():
    """Muestra la agenda de turnos en vista semanal.
    
    Parámetros opcionales:
    - fecha_inicio: primera fecha de la semana (YYYY-MM-DD). Si no se proporciona, usa la semana actual
    
    Retorna vista de agenda con semana completa (Lunes a Sábado) con turnos organizados por hora
    """
    fecha_inicio_str = request.args.get('fecha_inicio')
    
    # Parsear fecha si está presente
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        except ValueError:
            from datetime import date
            fecha_inicio = date.today()
    else:
        from datetime import date
        fecha_inicio = date.today()
    
    # Obtener estructura de agenda para la semana usando nuevo servicio
    datos_agenda = ObtenerAgendaService.obtener_semana_agenda(fecha_inicio)
    
    return render_template('turnos/agenda.html', **datos_agenda)


@main_bp.route('/pacientes/<int:paciente_id>/turnos')
@login_required
def listar_turnos_paciente(paciente_id: int):
    try:
        paciente = BuscarPacientesService.obtener_por_id(paciente_id)
    except PacienteNoEncontradoError:
        flash('Paciente no encontrado', 'error')
        return redirect(url_for('main.listar_pacientes'))

    pagina = request.args.get('pagina', 1, type=int)
    datos_paginacion = ListarTurnosService.listar_turnos_paciente_pagina(
        paciente_id=paciente_id,
        pagina=pagina,
        por_pagina=10
    )
    
    return render_template(
        'turnos/paciente_lista.html',
        paciente=paciente,
        turnos=datos_paginacion['turnos'],
        pagina_actual=datos_paginacion['pagina'],
        total_paginas=datos_paginacion['paginas_totales'],
        total=datos_paginacion['total'],
    )


@main_bp.route('/turnos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_turno():
    """Crear un nuevo turno con validación WTF."""
    form = TurnoForm()
    
    # Poblar select fields dinámicamente
    form.paciente_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(p.id, f'{p.nombre} {p.apellido} (DNI: {p.dni})') for p in Paciente.query.order_by(Paciente.apellido).all()]
    ]
    form.estado.choices = [
        ('Confirmado', 'Confirmado'),
        ('Pendiente', 'Pendiente'),
    ]
    
    # Pre-cargar paciente si viene en la URL
    paciente_id_url = request.args.get('paciente_id', type=int)
    if paciente_id_url and request.method == 'GET':
        form.paciente_id.data = paciente_id_url
    
    if form.validate_on_submit():
        try:
            # Calcular duración total en minutos
            duracion_total = (form.duracion_horas.data * 60) + form.duracion_minutos.data
            
            # Los datos ya están validados por WTF
            turno = AgendarTurnoService.execute(
                paciente_id=form.paciente_id.data,
                fecha=form.fecha.data,
                hora=form.hora.data,
                duracion=duracion_total,
                detalle=form.detalle.data,
            )
            flash('Turno creado exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=form.paciente_id.data))
        except (TurnoSolapamientoError, TurnoFechaInvalidaError, PacienteNoEncontradoError) as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear turno: {str(e)}', 'error')

    return render_template('turnos/nuevo.html', form=form)


@main_bp.route('/turnos/<int:turno_id>')
@login_required
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
    estados_permitidos = CambiarEstadoTurnoService.TRANSICIONES_VALIDAS.get(estado_actual, [])
    
    # Filtrar NoAtendido: solo se asigna automáticamente por el sistema, no manualmente por UI
    estados_permitidos = [e for e in estados_permitidos if e != 'NoAtendido']
    
    return render_template(
        'turnos/ver.html',
        turno=turno,
        cambios_estado=cambios_estado,
        estados_permitidos=estados_permitidos
    )


@main_bp.route('/turnos/<int:turno_id>/estado', methods=['POST'])
@login_required
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

    try:
        turno = CambiarEstadoTurnoService.execute(
            turno_id=turno_id,
            estado_nuevo=nuevo_estado,
            motivo='Cambio de estado desde interfaz web'
        )
        flash('Estado actualizado correctamente', 'success')
    except TurnoNoEncontradoError as e:
        flash(str(e), 'error')
    except TransicionEstadoInvalidaError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')

    return redirect(url_for('main.listar_turnos'))


@main_bp.route('/turnos/<int:turno_id>/eliminar', methods=['POST'])
@login_required
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
    try:
        resultado = EliminarTurnoService.execute(turno_id)
        flash(resultado['mensaje'], 'success')
    except TurnoNoEncontradoError as e:
        flash(str(e), 'error')
    except EstadoTurnoInvalidoError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_turnos'))


@main_bp.route('/turnos/<int:turno_id>/reagendar', methods=['POST'])
@login_required
def reagendar_turno(turno_id: int):
    """Reagendar un turno (cambiar fecha/hora).
    Solo se pueden reagendar turnos en estados no-finales (Pendiente, Confirmado).
    """
    try:
        nueva_fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        nueva_hora = datetime.strptime(request.form['hora'], '%H:%M').time()
        
        turno = EditarTurnoService.execute(
            turno_id=turno_id,
            fecha=nueva_fecha,
            hora=nueva_hora,
        )
        flash('Turno reagendado exitosamente', 'success')
    except EstadoFinalError as e:
        flash(str(e), 'error')
    except (TurnoSolapamientoError, TurnoFechaInvalidaError, TurnoNoEncontradoError) as e:
        flash(str(e), 'error')
    except ValueError as e:
        flash(f'Datos inválidos: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error inesperado al reagendar: {str(e)}', 'error')
    
    return redirect(url_for('main.ver_turno', turno_id=turno_id))
