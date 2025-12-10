from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import db
from app.models import Paciente, Turno, Estado, Operacion, Codigo, Localidad, ObraSocial
from app.services import BusquedaUtils
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal del sistema"""
    # Obtener estadísticas básicas
    stats = {
        'pacientes': Paciente.query.count(),
        'turnos': Turno.query.count(),
        'turnos_hoy': Turno.query.filter_by(fecha=date.today()).count(),
        'operaciones': Operacion.query.count()
    }
    
    # Turnos próximos (próximos 5)
    turnos_proximos = Turno.query.filter(Turno.fecha >= date.today()).order_by(Turno.fecha, Turno.hora).limit(5).all()
    
    return render_template('index.html', stats=stats, turnos_proximos=turnos_proximos)

@main_bp.route('/pacientes')
def listar_pacientes():
    """Lista todos los pacientes con funcionalidad de búsqueda"""
    # Obtener parámetro de búsqueda
    termino_busqueda = request.args.get('buscar', '').strip()
    
    if termino_busqueda:
        # Usar la búsqueda avanzada
        pacientes = BusquedaUtils.buscar_pacientes_simple(termino_busqueda)
    else:
        # Mostrar todos los pacientes
        pacientes = Paciente.query.all()
    
    return render_template('pacientes/lista.html', 
                         pacientes=pacientes, 
                         termino_busqueda=termino_busqueda)

@main_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
def crear_paciente():
    """Crear un nuevo paciente"""
    if request.method == 'POST':
        try:
            paciente = Paciente(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form['dni'],
                fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None,
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                direccion=request.form.get('direccion'),
                obra_social_id=int(request.form['obra_social_id']) if request.form.get('obra_social_id') else None,
                localidad_id=int(request.form['localidad_id']) if request.form.get('localidad_id') else None,
                observaciones=request.form.get('observaciones'),
                fecha_registro=date.today()
            )
            
            db.session.add(paciente)
            db.session.commit()
            flash('Paciente creado exitosamente', 'success')
            return redirect(url_for('main.listar_pacientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear paciente: {str(e)}', 'error')
    
    # Obtener datos para los selects
    obras_sociales = ObraSocial.query.order_by(ObraSocial.nombre).all()
    localidades = Localidad.query.order_by(Localidad.nombre).all()
    
    return render_template('pacientes/formulario.html', 
                         obras_sociales=obras_sociales, 
                         localidades=localidades)

@main_bp.route('/pacientes/<int:id>')
def ver_paciente(id):
    """Ver detalles de un paciente"""
    paciente = Paciente.query.get_or_404(id)
    
    # Calcular edad
    edad = None
    if paciente.fecha_nacimiento:
        edad = relativedelta(date.today(), paciente.fecha_nacimiento).years
    
    # Obtener turnos y operaciones del paciente
    turnos = Turno.query.filter_by(paciente_id=id).order_by(Turno.fecha.desc(), Turno.hora.desc()).all()
    operaciones = Operacion.query.filter_by(paciente_id=id).order_by(Operacion.fecha.desc()).all()
    
    # Estadísticas
    estadisticas = {
        'total_turnos': len(turnos),
        'total_operaciones': len(operaciones)
    }
    
    return render_template('pacientes/detalle.html', 
                         paciente=paciente, 
                         edad=edad,
                         turnos=turnos,
                         operaciones=operaciones,
                         estadisticas=estadisticas)

@main_bp.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_paciente(id):
    """Editar un paciente existente"""
    paciente = Paciente.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            paciente.nombre = request.form['nombre']
            paciente.apellido = request.form['apellido']
            paciente.dni = request.form['dni']
            paciente.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None
            paciente.telefono = request.form.get('telefono')
            paciente.email = request.form.get('email')
            paciente.direccion = request.form.get('direccion')
            paciente.obra_social_id = int(request.form['obra_social_id']) if request.form.get('obra_social_id') else None
            paciente.localidad_id = int(request.form['localidad_id']) if request.form.get('localidad_id') else None
            paciente.observaciones = request.form.get('observaciones')
            
            db.session.commit()
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=paciente.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar paciente: {str(e)}', 'error')
    
    # Obtener datos para los selects
    obras_sociales = ObraSocial.query.order_by(ObraSocial.nombre).all()
    localidades = Localidad.query.order_by(Localidad.nombre).all()
    
    return render_template('pacientes/formulario.html', 
                         paciente=paciente,
                         obras_sociales=obras_sociales, 
                         localidades=localidades)

@main_bp.route('/turnos')
def listar_turnos():
    """Lista todos los turnos"""
    # Obtener filtros de la URL
    fecha_filtro = request.args.get('fecha')
    
    query = Turno.query
    
    if fecha_filtro:
        fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
        query = query.filter_by(fecha=fecha_obj)
    else:
        # Por defecto, mostrar turnos de hoy en adelante
        query = query.filter(Turno.fecha >= date.today())
    
    turnos = query.order_by(Turno.fecha, Turno.hora).all()
    return render_template('turnos/lista.html', turnos=turnos, fecha_filtro=fecha_filtro)

@main_bp.route('/turnos/nuevo', methods=['GET', 'POST'])
def nuevo_turno():
    """Crear un nuevo turno"""
    if request.method == 'POST':
        try:
            turno = Turno(
                paciente_id=request.form['paciente_id'],
                fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
                hora=datetime.strptime(request.form['hora'], '%H:%M').time(),
                detalle=request.form.get('detalle'),
                estado=request.form.get('estado', 'Pendiente')
            )
            
            db.session.add(turno)
            db.session.commit()
            flash('Turno creado exitosamente', 'success')
            return redirect(url_for('main.listar_turnos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear turno: {str(e)}', 'error')
    
    pacientes = Paciente.query.all()
    estados = Estado.query.all()
    return render_template('turnos/nuevo.html', pacientes=pacientes, estados=estados)

@main_bp.route('/operaciones')
def listar_operaciones():
    """Lista todas las operaciones"""
    operaciones = Operacion.query.order_by(Operacion.fecha.desc()).all()
    return render_template('operaciones/lista.html', operaciones=operaciones)

@main_bp.route('/operaciones/nueva', methods=['GET', 'POST'])
def nueva_operacion():
    """Crear una nueva operación"""
    if request.method == 'POST':
        try:
            operacion = Operacion(
                paciente_id=request.form['paciente_id'],
                descripcion=request.form['descripcion'],
                monto=float(request.form['monto']),
                fecha=datetime.now(),
                codigo_id=request.form.get('codigo_id') if request.form.get('codigo_id') else None,
                observaciones=request.form.get('observaciones')
            )
            
            db.session.add(operacion)
            db.session.commit()
            flash('Operación registrada exitosamente', 'success')
            return redirect(url_for('main.listar_operaciones'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar operación: {str(e)}', 'error')
    
    pacientes = Paciente.query.all()
    codigos = Codigo.query.all()
    return render_template('operaciones/nueva.html', pacientes=pacientes, codigos=codigos)
