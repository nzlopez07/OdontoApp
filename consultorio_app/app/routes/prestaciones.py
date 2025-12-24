from datetime import datetime
from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.database import db
from app.forms import PrestacionForm
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
    """Crear nueva prestación con validación WTF."""
    form = PrestacionForm()
    
    # Poblar select fields dinámicamente
    form.paciente_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(p.id, f'{p.nombre} {p.apellido} (DNI: {p.dni})') for p in BuscarPacientesService.listar_todos()]
    ]
    
    # Pre-cargar paciente si viene en la URL
    paciente_id_url = request.args.get('paciente_id', type=int)
    if paciente_id_url and request.method == 'GET':
        form.paciente_id.data = paciente_id_url
    
    if form.validate_on_submit():
        try:
            # Obtener las prácticas seleccionadas desde el formulario JavaScript
            practica_ids = request.form.getlist('practica_ids[]', type=int)
            
            if not practica_ids:
                flash('Debe seleccionar al menos una práctica', 'warning')
                # Pasar datos al template para preservar estado
                return render_template(
                    'prestaciones/nueva.html', 
                    form=form,
                    practica_ids_str=','.join(str(id) for id in practica_ids)
                )
            
            # El monto viene como HiddenField calculado por JavaScript
            monto_str = form.monto.data or '0'
            try:
                monto = Decimal(str(monto_str))
            except:
                monto = Decimal('0')
            
            # Procesar observaciones: convertir cadena vacía a None
            observaciones = form.observaciones.data
            if observaciones and isinstance(observaciones, str):
                observaciones = observaciones.strip() or None
            else:
                observaciones = None
            
            prestacion = CrearPrestacionService.execute({
                'paciente_id': form.paciente_id.data,
                'descripcion': form.descripcion.data,
                'observaciones': observaciones,
                'practicas': practica_ids,  # Lista de IDs de prácticas
                'descuento_porcentaje': float(form.descuento_porcentaje.data or 0),
                'descuento_fijo': float(form.descuento_fijo.data or 0),
            })
            flash('Prestación registrada exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=form.paciente_id.data))
        except (PacienteNoEncontradoError, PracticaNoEncontradaError, DatosInvalidosError) as e:
            flash(str(e), 'error')
            # Pasar datos al template para preservar estado
            practica_ids = request.form.getlist('practica_ids[]', type=int)
            return render_template(
                'prestaciones/nueva.html', 
                form=form,
                practica_ids_str=','.join(str(id) for id in practica_ids)
            )
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar prestación: {str(e)}', 'error')
            practica_ids = request.form.getlist('practica_ids[]', type=int)
            return render_template(
                'prestaciones/nueva.html', 
                form=form,
                practica_ids_str=','.join(str(id) for id in practica_ids)
            )

    return render_template('prestaciones/nueva.html', form=form)
