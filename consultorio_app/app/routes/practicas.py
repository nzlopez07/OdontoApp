from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.forms import PracticaForm
from app.services.practica import (
    ListarPracticasService,
    CrearPracticaService,
    EditarPracticaService,
    EliminarPracticaService,
)
from app.services.common import (
    PracticaNoEncontradaError,
    PracticaConDependenciasError,
    DatosInvalidosError,
)
from app.models import ObraSocial
from . import main_bp


@main_bp.route('/practicas')
@login_required
def listar_practicas():
    proveedor_filter = request.args.get('proveedor', '').strip()
    
    if proveedor_filter == 'IPSS':
        ipss = ObraSocial.query.filter_by(nombre='IPSS').first()
        obra_social_id = ipss.id if ipss else None
        practicas = ListarPracticasService.listar_por_proveedor(obra_social_id) if obra_social_id else []
        titulo = 'IPSS'
    elif proveedor_filter == 'SANCOR':
        sancor = ObraSocial.query.filter_by(nombre='SANCOR SALUD').first()
        obra_social_id = sancor.id if sancor else None
        practicas = ListarPracticasService.listar_por_proveedor(obra_social_id) if obra_social_id else []
        titulo = 'SANCOR SALUD'
    else:
        practicas = ListarPracticasService.listar_por_proveedor()
        titulo = 'Particular'
    
    return render_template('practicas/lista.html', practicas=practicas, titulo=titulo, proveedor_filter=proveedor_filter)


@main_bp.route('/practicas/nueva', methods=['GET', 'POST'])
@login_required
def crear_practica():
    form = PracticaForm()
    
    # Populate dynamic choices
    obras_sociales = ObraSocial.query.all()
    form.obra_social_id.choices = [(0, 'Seleccionar...')] + [(o.id, o.nombre) for o in obras_sociales]
    
    if form.validate_on_submit():
        try:
            # Determinar proveedor_tipo automáticamente según obra social seleccionada
            obra_social_id = form.obra_social_id.data if form.obra_social_id.data else None
            proveedor_tipo = 'OBRA_SOCIAL' if obra_social_id else 'PARTICULAR'
            
            practica = CrearPracticaService.execute({
                'codigo': form.codigo.data,
                'descripcion': form.descripcion.data,
                'proveedor_tipo': proveedor_tipo,
                'obra_social_id': obra_social_id,
                'monto_unitario': float(form.monto_unitario.data)
            })
            flash('Práctica creada exitosamente', 'success')
            return redirect(url_for('main.listar_practicas'))
        except DatosInvalidosError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear práctica: {str(e)}', 'error')
    
    return render_template('practicas/formulario.html', form=form, obras_sociales=obras_sociales)


@main_bp.route('/practicas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_practica(id: int):
    try:
        practica = ListarPracticasService.obtener_por_id(id)
    except PracticaNoEncontradaError:
        flash('Práctica no encontrada', 'error')
        return redirect(url_for('main.listar_practicas'))
    
    form = PracticaForm()
    obras_sociales = ObraSocial.query.all()
    form.obra_social_id.choices = [(0, 'Seleccionar...')] + [(o.id, o.nombre) for o in obras_sociales]
    
    if form.validate_on_submit():
        try:
            # Determinar proveedor_tipo automáticamente según obra social seleccionada
            obra_social_id = form.obra_social_id.data if form.obra_social_id.data else None
            proveedor_tipo = 'OBRA_SOCIAL' if obra_social_id else 'PARTICULAR'
            
            practica = EditarPracticaService.execute(id, {
                'codigo': form.codigo.data,
                'descripcion': form.descripcion.data,
                'proveedor_tipo': proveedor_tipo,
                'obra_social_id': obra_social_id,
                'monto_unitario': float(form.monto_unitario.data)
            })
            flash('Práctica actualizada exitosamente', 'success')
            return redirect(url_for('main.listar_practicas'))
        except PracticaNoEncontradaError as e:
            flash(str(e), 'error')
        except DatosInvalidosError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar práctica: {str(e)}', 'error')
    elif request.method == 'GET':
        # Pre-populate form on GET
        form.codigo.data = practica.codigo
        form.descripcion.data = practica.descripcion
        form.obra_social_id.data = practica.obra_social_id or 0
        form.monto_unitario.data = practica.monto_unitario
    
    return render_template('practicas/formulario.html', form=form, practica=practica, obras_sociales=obras_sociales)


@main_bp.route('/practicas/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_practica(id: int):
    try:
        resultado = EliminarPracticaService.execute(id)
        flash(resultado['mensaje'], 'success')
    except PracticaNoEncontradaError as e:
        flash(str(e), 'error')
    except PracticaConDependenciasError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al eliminar práctica: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_practicas'))
