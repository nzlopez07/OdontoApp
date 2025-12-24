from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
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
    obras_sociales = ObraSocial.query.all()
    
    if request.method == 'POST':
        try:
            proveedor_tipo = request.form.get('proveedor_tipo', 'PARTICULAR')
            obra_social_id = None
            if proveedor_tipo == 'OBRA_SOCIAL':
                obra_social_id_str = request.form.get('obra_social_id')
                obra_social_id = int(obra_social_id_str) if obra_social_id_str else None
            
            practica = CrearPracticaService.execute({
                'codigo': request.form['codigo'],
                'descripcion': request.form['descripcion'],
                'proveedor_tipo': proveedor_tipo,
                'obra_social_id': obra_social_id,
                'monto_unitario': float(request.form['monto_unitario'])
            })
            flash('Práctica creada exitosamente', 'success')
            return redirect(url_for('main.listar_practicas'))
        except DatosInvalidosError as e:
            flash(str(e), 'error')
        except ValueError as e:
            flash(f'Datos inválidos: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al crear práctica: {str(e)}', 'error')
    
    return render_template('practicas/formulario.html', obras_sociales=obras_sociales)


@main_bp.route('/practicas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_practica(id: int):
    try:
        practica = ListarPracticasService.obtener_por_id(id)
    except PracticaNoEncontradaError:
        flash('Práctica no encontrada', 'error')
        return redirect(url_for('main.listar_practicas'))
    
    obras_sociales = ObraSocial.query.all()
    
    if request.method == 'POST':
        try:
            proveedor_tipo = request.form.get('proveedor_tipo', 'PARTICULAR')
            obra_social_id = None
            if proveedor_tipo == 'OBRA_SOCIAL':
                obra_social_id_str = request.form.get('obra_social_id')
                obra_social_id = int(obra_social_id_str) if obra_social_id_str else None
            
            practica = EditarPracticaService.execute(id, {
                'codigo': request.form['codigo'],
                'descripcion': request.form['descripcion'],
                'proveedor_tipo': proveedor_tipo,
                'obra_social_id': obra_social_id,
                'monto_unitario': float(request.form['monto_unitario'])
            })
            flash('Práctica actualizada exitosamente', 'success')
            return redirect(url_for('main.listar_practicas'))
        except (PracticaNoEncontradaError, DatosInvalidosError) as e:
            flash(str(e), 'error')
        except ValueError as e:
            flash(f'Datos inválidos: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al actualizar práctica: {str(e)}', 'error')
    
    return render_template('practicas/formulario.html', practica=practica, obras_sociales=obras_sociales)


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
