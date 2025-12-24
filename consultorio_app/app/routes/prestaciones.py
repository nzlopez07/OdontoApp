from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.database import db
from app.services.prestacion import ListarPrestacionesService, CrearPrestacionService
from app.services.paciente import BuscarPacientesService
from app.services.practica import ListarPracticasService
from app.services.common import (
    PacienteNoEncontradoError,
    PracticaNoEncontradaError,
    DatosInvalidosError,
)
from . import main_bp


@main_bp.route('/prestaciones')
@login_required
def listar_prestaciones():
    prestaciones = ListarPrestacionesService.listar_todas()
    return render_template('prestaciones/lista.html', prestaciones=prestaciones)


@main_bp.route('/pacientes/<int:paciente_id>/prestaciones')
@login_required
def listar_prestaciones_paciente(paciente_id: int):
    try:
        paciente = BuscarPacientesService.obtener_por_id(paciente_id)
    except PacienteNoEncontradoError:
        flash('Paciente no encontrado', 'error')
        return redirect(url_for('main.listar_pacientes'))

    pagina = request.args.get('pagina', 1, type=int)
    
    # Preparar filtros opcionales
    descripcion = request.args.get('descripcion', '').strip() or None
    monto_min_str = request.args.get('monto_min', '').strip()
    monto_max_str = request.args.get('monto_max', '').strip()
    monto_min = float(monto_min_str) if monto_min_str else None
    monto_max = float(monto_max_str) if monto_max_str else None
    
    datos_paginacion = ListarPrestacionesService.listar_por_paciente(
        paciente_id=paciente_id,
        pagina=pagina,
        por_pagina=10,
        descripcion=descripcion,
        monto_min=monto_min,
        monto_max=monto_max,
    )
    
    return render_template(
        'prestaciones/paciente_lista.html',
        paciente=paciente,
        prestaciones=datos_paginacion['items'],
        pagina_actual=datos_paginacion['pagina_actual'],
        total_paginas=datos_paginacion['total_paginas'],
        total=datos_paginacion['total'],
        filtros=datos_paginacion['filtros_aplicados'],
    )


@main_bp.route('/prestaciones/nueva', methods=['GET', 'POST'])
@login_required
def nueva_prestacion():
    paciente_id = request.args.get('paciente_id')
    
    if request.method == 'POST':
        try:
            paciente_id_form = int(request.form['paciente_id'])
            practicas_ids = request.form.getlist('practica_ids[]')
            
            # Convertir IDs a lista de enteros
            practicas_list = [int(pid) for pid in practicas_ids if pid.strip()]
            
            # Obtener descuentos
            desc_pct_str = request.form.get('descuento_porcentaje', '').strip()
            desc_fijo_str = request.form.get('descuento_fijo', '').strip()
            desc_pct = float(desc_pct_str) if desc_pct_str else 0
            desc_fijo = float(desc_fijo_str) if desc_fijo_str else 0
            
            prestacion = CrearPrestacionService.execute({
                'paciente_id': paciente_id_form,
                'descripcion': request.form['descripcion'],
                'observaciones': request.form.get('observaciones'),
                'practicas': practicas_list,
                'descuento_porcentaje': desc_pct,
                'descuento_fijo': desc_fijo,
            })
            flash('Prestación registrada exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=paciente_id_form))
        except (PacienteNoEncontradoError, PracticaNoEncontradaError, DatosInvalidosError) as e:
            flash(str(e), 'error')
        except ValueError as e:
            flash(f'Datos inválidos: {str(e)}', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar prestación: {str(e)}', 'error')

    pacientes = BuscarPacientesService.listar_todos()
    practicas_disponibles = []
    if paciente_id:
        try:
            paciente_id_int = int(paciente_id)
            # Obtener todas las prácticas (mejorar luego con filtro por obra social del paciente)
            practicas_disponibles = ListarPracticasService.listar_todas()
        except (ValueError, TypeError):
            paciente_id = None
    
    return render_template('prestaciones/nueva.html', pacientes=pacientes, practicas=practicas_disponibles, paciente_id=paciente_id)
