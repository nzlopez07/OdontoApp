from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import render_template, request, redirect, url_for, flash
from app.models import Prestacion
from app.services.paciente_service import PacienteService
from app.services.turno_service import TurnoService
from . import main_bp


@main_bp.route('/pacientes')
def listar_pacientes():
    """Lista todos los pacientes con funcionalidad de búsqueda.
    
    ---
    tags:
      - Pacientes
    parameters:
      - name: buscar
        in: query
        type: string
        description: Término de búsqueda por nombre, apellido o DNI
    responses:
      200:
        description: Lista de pacientes obtenida exitosamente
    """
    termino_busqueda = request.args.get('buscar', '').strip()
    pacientes = PacienteService.listar_pacientes(termino_busqueda)
    return render_template(
      'pacientes/lista.html',
      pacientes=pacientes,
      termino_busqueda=termino_busqueda,
    )


@main_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
def crear_paciente():
    """Crear un nuevo paciente.
    
    ---
    tags:
      - Pacientes
    parameters:
      - name: nombre
        in: form
        type: string
        required: true
      - name: apellido
        in: form
        type: string
        required: true
      - name: dni
        in: form
        type: string
        required: true
      - name: fecha_nac
        in: form
        type: string
        format: date
      - name: telefono
        in: form
        type: string
      - name: direccion
        in: form
        type: string
      - name: obra_social_id
        in: form
        type: integer
      - name: localidad_id
        in: form
        type: integer
      - name: carnet
        in: form
        type: string
      - name: titular
        in: form
        type: string
      - name: parentesco
        in: form
        type: string
      - name: lugar_trabajo
        in: form
        type: string
      - name: barrio
        in: form
        type: string
    responses:
      200:
        description: Formulario para crear paciente (GET) o paciente creado (POST)
      302:
        description: Redirección después de crear paciente exitosamente
    """
    obras_sociales = PacienteService.listar_obras_sociales()
    localidades = PacienteService.listar_localidades()

    if request.method == 'POST':
        try:
            fecha_nac = datetime.strptime(request.form['fecha_nac'], '%Y-%m-%d').date() if request.form.get('fecha_nac') else None
            PacienteService.crear_paciente({
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'dni': request.form['dni'],
                'fecha_nac': fecha_nac,
                'telefono': request.form.get('telefono'),
                'direccion': request.form.get('direccion'),
                'obra_social_id': int(request.form['obra_social_id']) if request.form.get('obra_social_id') else None,
                'localidad_id': int(request.form['localidad_id']) if request.form.get('localidad_id') else None,
                'nro_afiliado': request.form.get('carnet'),
                'titular': request.form.get('titular'),
                'parentesco': request.form.get('parentesco'),
                'lugar_trabajo': request.form.get('lugar_trabajo'),
                'barrio': request.form.get('barrio'),
            })
            flash('Paciente creado exitosamente', 'success')
            return redirect(url_for('main.listar_pacientes'))
        except Exception as e:
            flash(f'Error al crear paciente: {str(e)}', 'error')

    return render_template(
        'pacientes/formulario.html',
        obras_sociales=obras_sociales,
        localidades=localidades,
    )


@main_bp.route('/pacientes/<int:id>')
def ver_paciente(id: int):
    """Ver detalles de un paciente.
    
    ---
    tags:
      - Pacientes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del paciente
    responses:
      200:
        description: Detalles del paciente obtenidos exitosamente
      404:
        description: Paciente no encontrado
    """
    paciente, turnos, prestaciones, edad = PacienteService.obtener_detalle(id)
    if not paciente:
        return redirect(url_for('main.listar_pacientes'))

    estadisticas = {
        'total_turnos': len(turnos),
        'total_prestaciones': len(prestaciones),
    }

    return render_template(
        'pacientes/detalle.html',
        paciente=paciente,
        edad=edad,
        turnos=turnos,
        prestaciones=prestaciones,
        estadisticas=estadisticas,
    )


@main_bp.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_paciente(id: int):
    """Editar un paciente existente."""
    paciente = PacienteService.obtener_paciente(id)
    if not paciente:
        return redirect(url_for('main.listar_pacientes'))

    if request.method == 'POST':
        try:
            fecha_nac = datetime.strptime(request.form['fecha_nac'], '%Y-%m-%d').date() if request.form.get('fecha_nac') else None
            PacienteService.actualizar_paciente(paciente, {
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'dni': request.form['dni'],
                'fecha_nac': fecha_nac,
                'telefono': request.form.get('telefono'),
                'direccion': request.form.get('direccion'),
                'obra_social_id': int(request.form['obra_social_id']) if request.form.get('obra_social_id') else None,
                'localidad_id': int(request.form['localidad_id']) if request.form.get('localidad_id') else None,
                'nro_afiliado': request.form.get('carnet'),
                'titular': request.form.get('titular'),
                'parentesco': request.form.get('parentesco'),
                'lugar_trabajo': request.form.get('lugar_trabajo'),
                'barrio': request.form.get('barrio'),
            })
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=paciente.id))
        except Exception as e:
            flash(f'Error al actualizar paciente: {str(e)}', 'error')

    obras_sociales = PacienteService.listar_obras_sociales()
    localidades = PacienteService.listar_localidades()

    return render_template(
        'pacientes/formulario.html',
        paciente=paciente,
        obras_sociales=obras_sociales,
        localidades=localidades,
    )
