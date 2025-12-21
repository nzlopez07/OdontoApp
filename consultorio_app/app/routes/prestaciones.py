from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from app.database import db
from app.services.prestacion_service import PrestacionService
from app.services.paciente_service import PacienteService
from . import main_bp


@main_bp.route('/prestaciones')
def listar_prestaciones():
    prestaciones = PrestacionService.listar_prestaciones()
    return render_template('prestaciones/lista.html', prestaciones=prestaciones)


@main_bp.route('/pacientes/<int:paciente_id>/prestaciones')
def listar_prestaciones_paciente(paciente_id: int):
    paciente = PacienteService.obtener_paciente(paciente_id)
    if not paciente:
        flash('Paciente no encontrado', 'error')
        return redirect(url_for('main.listar_pacientes'))

    pagina = request.args.get('pagina', 1, type=int)
    filtros = {
        'descripcion': request.args.get('descripcion', '').strip(),
        'monto_min': request.args.get('monto_min', '').strip(),
        'monto_max': request.args.get('monto_max', '').strip(),
    }
    
    datos_paginacion = PrestacionService.listar_prestaciones_por_paciente_pagina(
        paciente_id, pagina=pagina, por_pagina=10, filtros=filtros if any(filtros.values()) else None
    )
    
    return render_template(
        'prestaciones/paciente_lista.html',
        paciente=paciente,
        prestaciones=datos_paginacion['items'],
        pagina_actual=datos_paginacion['pagina_actual'],
        total_paginas=datos_paginacion['total_paginas'],
        total=datos_paginacion['total'],
        filtros=filtros,
    )


@main_bp.route('/prestaciones/nueva', methods=['GET', 'POST'])
def nueva_prestacion():
    paciente_id = request.args.get('paciente_id')
    
    if request.method == 'POST':
        try:
            paciente_id = int(request.form['paciente_id'])
            practicas_ids = request.form.getlist('practica_ids[]')
            
            practicas = []
            for pid in practicas_ids:
                if pid.strip():
                    practicas.append({'practica_id': int(pid)})
            
            PrestacionService.crear_prestacion({
                'paciente_id': paciente_id,
                'descripcion': request.form['descripcion'],
                'observaciones': request.form.get('observaciones'),
                'practicas': practicas,
                'descuento_porcentaje': request.form.get('descuento_porcentaje'),
                'descuento_fijo': request.form.get('descuento_fijo'),
            })
            flash('Prestación registrada exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=paciente_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar prestación: {str(e)}', 'error')

    pacientes = PrestacionService.listar_pacientes()
    practicas_disponibles = []
    if paciente_id:
        try:
            paciente_id = int(paciente_id)
            practicas_disponibles = PrestacionService.listar_practicas_para_paciente(paciente_id)
        except (ValueError, TypeError):
            paciente_id = None
    
    return render_template('prestaciones/nueva.html', pacientes=pacientes, practicas=practicas_disponibles, paciente_id=paciente_id)
