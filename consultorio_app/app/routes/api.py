"""
API endpoints JSON para integración con Swagger/OpenAPI.
Todos los endpoints retornan JSON para integración con herramientas externas.
"""
from datetime import datetime, date
from flask import jsonify, request, session
from flask_login import login_required
from sqlalchemy.orm import joinedload
from app.database.session import DatabaseSession
from app.models import Paciente, Turno, Prestacion, Estado, CambioEstado
from app.services.practica import ListarPracticasService
from app.services.paciente import BuscarPacientesService
from app.services.common import PacienteNoEncontradoError
from . import main_bp


# ===================== UTILIDADES =====================

def _actualizar_no_atendidos(session):
    """Marca como NoAtendido los turnos vencidos que no fueron atendidos."""
    ahora = datetime.now()
    hoy = date.today()
    estados = {
        e.nombre: e.id
        for e in session.query(Estado).filter(Estado.nombre.in_([
            'Atendido', 'NoAtendido', 'Cancelado'
        ])).all()
    }

    if 'NoAtendido' not in estados:
        print('[api] Estado "NoAtendido" no encontrado; no se actualizaron turnos.')
        return 0

    filtros = [Turno.estado_id.is_(None)]
    ids_excluir = [eid for name, eid in estados.items() if name in ['Atendido', 'NoAtendido', 'Cancelado']]
    if ids_excluir:
        filtros.append(~Turno.estado_id.in_(ids_excluir))

    vencidos = (
        session.query(Turno)
        .options(joinedload(Turno.paciente), joinedload(Turno.estado_obj))
        .filter(*filtros)
        .all()
    )
    
    cambios = 0
    for turno in vencidos:
        es_vencido = False
        
        if turno.fecha < hoy:
            es_vencido = True
        elif turno.fecha == hoy and turno.hora:
            turno_datetime = datetime.combine(turno.fecha, turno.hora)
            if turno_datetime < ahora:
                es_vencido = True
        
        if es_vencido:
            turno.estado_id = estados.get('NoAtendido')
            turno.estado = 'NoAtendido'
            cambios += 1
    
    if cambios:
        session.commit()
    
    return cambios


# ===================== PACIENTES API =====================

@main_bp.route('/api/pacientes')
@login_required
def api_listar_pacientes():
    """Get all patients
    ---
    tags:
      - Pacientes
    parameters:
      - name: buscar
        in: query
        type: string
    responses:
      200:
        description: List of patients
    """
    termino_busqueda = request.args.get('buscar', '').strip()
    if termino_busqueda:
      pacientes = BuscarPacientesService.buscar(termino_busqueda)
    else:
        pacientes = Paciente.query.all()

    pacientes_data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'apellido': p.apellido,
            'dni': p.dni,
            'fecha_nac': p.fecha_nac.isoformat() if p.fecha_nac else None,
            'telefono': p.telefono,
            'direccion': p.direccion,
            'localidad_id': p.localidad_id,
            'obra_social_id': p.obra_social_id,
        }
        for p in pacientes
    ]

    return jsonify({'pacientes': pacientes_data})


@main_bp.route('/api/pacientes/<int:id>')
@login_required
def api_ver_paciente(id: int):
    """Get patient details
    ---
    tags:
      - Pacientes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Patient details
      404:
        description: Patient not found
    """
    paciente = Paciente.query.get_or_404(id)

    from dateutil.relativedelta import relativedelta
    edad = None
    if paciente.fecha_nac:
        edad = relativedelta(date.today(), paciente.fecha_nac).years

    turnos = Turno.query.filter_by(paciente_id=id).order_by(Turno.fecha.desc()).count()
    prestaciones = Prestacion.query.filter_by(paciente_id=id).count()

    return jsonify({
        'id': paciente.id,
        'nombre': paciente.nombre,
        'apellido': paciente.apellido,
        'dni': paciente.dni,
        'fecha_nac': paciente.fecha_nac.isoformat() if paciente.fecha_nac else None,
        'edad': edad,
        'telefono': paciente.telefono,
        'direccion': paciente.direccion,
        'turnos_cantidad': turnos,
        'prestaciones_cantidad': prestaciones,
    })


# ===================== TURNOS API =====================

@main_bp.route('/api/turnos')
@login_required
def api_listar_turnos():
    """Get all appointments
    ---
    tags:
      - Turnos
    parameters:
      - name: fecha
        in: query
        type: string
        format: date
      - name: buscar
        in: query
        type: string
      - name: estado
        in: query
        type: string
    responses:
      200:
        description: List of appointments
    """
    session = DatabaseSession.get_instance().session
    
    # Actualizar turnos vencidos antes de listar
    _actualizar_no_atendidos(session)
    
    fecha_filtro = request.args.get('fecha')
    termino = request.args.get('buscar', '').strip()
    estado_filtro = request.args.get('estado', '').strip()

    query = session.query(Turno).options(joinedload(Turno.paciente), joinedload(Turno.estado_obj))

    if fecha_filtro:
        fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
        query = query.filter(Turno.fecha == fecha_obj)
    else:
        query = query.filter(Turno.fecha >= date.today())

    if estado_filtro:
      estado_obj = session.query(Estado).filter_by(nombre=estado_filtro).first()
      if not estado_obj:
        return jsonify({'turnos': [], 'cantidad': 0})
      query = query.filter(Turno.estado_id == estado_obj.id)

    if termino:
        like_term = f"%{termino.lower()}%"
        query = query.join(Paciente).filter(
            (Paciente.nombre.ilike(like_term)) |
            (Paciente.apellido.ilike(like_term)) |
            (Paciente.dni.ilike(like_term))
        )

    turnos = query.order_by(Turno.fecha, Turno.hora).all()

    turnos_data = [
        {
            'id': t.id,
            'fecha': t.fecha.isoformat(),
            'hora': t.hora.isoformat() if t.hora else None,
            'estado': t.estado_nombre,
            'detalle': t.detalle,
            'paciente_id': t.paciente_id,
            'paciente_nombre': f"{t.paciente.nombre} {t.paciente.apellido}" if t.paciente else '',
        }
        for t in turnos
    ]

    return jsonify({'turnos': turnos_data, 'cantidad': len(turnos_data)})


@main_bp.route('/api/turnos/<int:id>')
@login_required
def api_ver_turno(id: int):
    """Get appointment details
    ---
    tags:
      - Turnos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Appointment details
      404:
        description: Appointment not found
    """
    session = DatabaseSession.get_instance().session
    
    # Actualizar turnos vencidos antes de retornar detalles
    _actualizar_no_atendidos(session)
    
    turno = Turno.query.options(joinedload(Turno.paciente), joinedload(Turno.estado_obj)).get_or_404(id)

    cambios = CambioEstado.query.filter_by(turno_id=id).order_by(CambioEstado.fecha_cambio.desc()).all()

    return jsonify({
        'id': turno.id,
        'fecha': turno.fecha.isoformat(),
        'hora': turno.hora.isoformat() if turno.hora else None,
        'estado': turno.estado_nombre,
        'detalle': turno.detalle,
        'paciente': {
            'id': turno.paciente.id,
            'nombre': turno.paciente.nombre,
            'apellido': turno.paciente.apellido,
            'dni': turno.paciente.dni,
        },
        'cambios_estado': [
            {
                'id': c.id,
                'estado_anterior': c.estado_anterior,
                'estado_nuevo': c.estado_nuevo,
                'fecha_cambio': c.fecha_cambio.isoformat(),
                'motivo': c.motivo,
            }
            for c in cambios
        ],
    })


# ===================== PRESTACIONES API =====================

@main_bp.route('/api/prestaciones')
@login_required
def api_listar_prestaciones():
    """Get all prestaciones
    ---
    tags:
      - Prestaciones
    parameters:
      - name: paciente_id
        in: query
        type: integer
    responses:
      200:
        description: List of operations
    """
    paciente_id = request.args.get('paciente_id', type=int)
    
    query = Prestacion.query.options(joinedload(Prestacion.paciente))
    
    if paciente_id:
        query = query.filter(Prestacion.paciente_id == paciente_id)
    
    prestaciones = query.order_by(Prestacion.fecha.desc()).all()

    prestaciones_data = [
        {
            'id': o.id,
            'descripcion': o.descripcion,
            'monto': float(o.monto) if o.monto else 0,
            'fecha': o.fecha.isoformat() if o.fecha else None,
            'paciente_id': o.paciente_id,
            'paciente_nombre': f"{o.paciente.nombre} {o.paciente.apellido}" if o.paciente else '',
        }
        for o in prestaciones
    ]

    return jsonify({'prestaciones': prestaciones_data, 'cantidad': len(prestaciones_data)})


@main_bp.route('/api/prestaciones/<int:id>')
@login_required
def api_ver_prestacion(id: int):
    """Get prestacion details
    ---
    tags:
      - Prestaciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Operation details
      404:
        description: Operation not found
    """
    prestacion = Prestacion.query.get_or_404(id)

    return jsonify({
        'id': prestacion.id,
        'descripcion': prestacion.descripcion,
        'monto': float(prestacion.monto) if prestacion.monto else 0,
        'fecha': prestacion.fecha.isoformat() if prestacion.fecha else None,
        'observaciones': prestacion.observaciones,
        'paciente': {
            'id': prestacion.paciente.id,
            'nombre': prestacion.paciente.nombre,
            'apellido': prestacion.paciente.apellido,
            'dni': prestacion.paciente.dni,
        },
    })


# ===================== ESTADOS API =====================

@main_bp.route('/api/estados')
@login_required
def api_listar_estados():
    """Get available appointment statuses
    ---
    tags:
      - Configuración
    responses:
      200:
        description: List of available statuses
    """
    estados = ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']
    return jsonify({'estados': estados})


@main_bp.route('/api/turnos/sync/actualizar-vencidos', methods=['POST'])
@login_required
def api_actualizar_turnos_vencidos():
    """Fuerza la actualización de turnos vencidos a NoAtendido
    ---
    tags:
      - Turnos
    responses:
      200:
        description: Turnos actualizados
    """
    session = DatabaseSession.get_instance().session
    cambios = _actualizar_no_atendidos(session)
    
    return jsonify({
        'mensaje': f'Se actualizaron {cambios} turnos a NoAtendido',
        'cantidad': cambios
    })


@main_bp.route('/api/pacientes/<int:paciente_id>/practicas')
@login_required
def api_listar_practicas_paciente(paciente_id: int):
  """Listar prácticas disponibles para un paciente según su obra social
  ---
  tags:
    - Practicas
  parameters:
    - name: paciente_id
      in: path
      type: integer
      required: true
      description: ID del paciente
  responses:
    200:
      description: Lista de prácticas recomendadas para la obra social del paciente
    404:
      description: Paciente no encontrado
  """
  try:
    paciente = BuscarPacientesService.obtener_por_id(paciente_id)
  except PacienteNoEncontradoError:
    return jsonify({'error': 'Paciente no encontrado'}), 404

  obra_social_id = paciente.obra_social_id
  practicas = ListarPracticasService.listar_por_proveedor(obra_social_id)

  practicas_data = [
    {
      'id': p.id,
      'codigo': p.codigo,
      'descripcion': p.descripcion,
      'proveedor_tipo': p.proveedor_tipo,
      'monto_unitario': p.monto_unitario,
    }
    for p in practicas
  ]
  return jsonify({'paciente_id': paciente_id, 'practicas': practicas_data, 'obra_social_id': obra_social_id})
