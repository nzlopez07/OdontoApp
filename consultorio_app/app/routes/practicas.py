from flask import render_template, request, redirect, url_for, flash
from app.services.practica_service import PracticaService
from app.models import ObraSocial
from . import main_bp


@main_bp.route('/practicas')
def listar_practicas():
    proveedor_filter = request.args.get('proveedor', '').strip()
    
    if proveedor_filter == 'IPSS':
        ipss = ObraSocial.query.filter_by(nombre='IPSS').first()
        obra_social_id = ipss.id if ipss else None
        practicas = PracticaService.listar_por_proveedor(obra_social_id) if obra_social_id else []
        titulo = 'IPSS'
    elif proveedor_filter == 'SANCOR':
        sancor = ObraSocial.query.filter_by(nombre='SANCOR SALUD').first()
        obra_social_id = sancor.id if sancor else None
        practicas = PracticaService.listar_por_proveedor(obra_social_id) if obra_social_id else []
        titulo = 'SANCOR SALUD'
    else:
        practicas = PracticaService.listar_por_proveedor()
        titulo = 'Particular'
    
    return render_template('practicas/lista.html', practicas=practicas, titulo=titulo, proveedor_filter=proveedor_filter)


@main_bp.route('/practicas/nueva', methods=['GET', 'POST'])
def crear_practica():
    obras_sociales = ObraSocial.query.all()
    
    if request.method == 'POST':
        try:
            proveedor_tipo = request.form.get('proveedor_tipo', 'PARTICULAR')
            obra_social_id = None
            if proveedor_tipo == 'OBRA_SOCIAL':
                obra_social_id = request.form.get('obra_social_id')
            
            PracticaService.crear_practica({
                'codigo': request.form['codigo'],
                'descripcion': request.form['descripcion'],
                'proveedor_tipo': proveedor_tipo,
                'obra_social_id': obra_social_id,
                'monto_unitario': request.form['monto_unitario']
            })
            flash('Práctica creada exitosamente', 'success')
            return redirect(url_for('main.listar_practicas'))
        except Exception as e:
            flash(f'Error al crear práctica: {str(e)}', 'error')
    
    return render_template('practicas/formulario.html', obras_sociales=obras_sociales)


@main_bp.route('/practicas/<int:id>/editar', methods=['GET', 'POST'])
def editar_practica(id: int):
    practica = PracticaService.obtener_practica(id)
    if not practica:
        return redirect(url_for('main.listar_practicas'))
    
    obras_sociales = ObraSocial.query.all()
    
    if request.method == 'POST':
        try:
            proveedor_tipo = request.form.get('proveedor_tipo', 'PARTICULAR')
            obra_social_id = None
            if proveedor_tipo == 'OBRA_SOCIAL':
                obra_social_id = request.form.get('obra_social_id')
            
            PracticaService.actualizar_practica(id, {
                'codigo': request.form['codigo'],
                'descripcion': request.form['descripcion'],
                'proveedor_tipo': proveedor_tipo,
                'obra_social_id': obra_social_id,
                'monto_unitario': request.form['monto_unitario']
            })
            flash('Práctica actualizada exitosamente', 'success')
            return redirect(url_for('main.listar_practicas'))
        except Exception as e:
            flash(f'Error al actualizar práctica: {str(e)}', 'error')
    
    return render_template('practicas/formulario.html', practica=practica, obras_sociales=obras_sociales)


@main_bp.route('/practicas/<int:id>/eliminar', methods=['POST'])
def eliminar_practica(id: int):
    try:
        if PracticaService.eliminar_practica(id):
            flash('Práctica eliminada exitosamente', 'success')
        else:
            flash('Práctica no encontrada', 'error')
    except Exception as e:
        flash(f'Error al eliminar práctica: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_practicas'))
