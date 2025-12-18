from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from app.services.prestacion_service import PrestacionService
from . import main_bp


@main_bp.route('/prestaciones')
def listar_prestaciones():
    """Lista todas las prestaciones.
    ---
    tags:
      - Prestaciones
    responses:
      200:
        description: Lista de prestaciones obtenida exitosamente
    """
    prestaciones = PrestacionService.listar_prestaciones()
    return render_template('prestaciones/lista.html', prestaciones=prestaciones)


@main_bp.route('/prestaciones/nueva', methods=['GET', 'POST'])
def nueva_prestacion():
    """Crear una nueva prestación.
    ---
    tags:
      - Prestaciones
    parameters:
      - name: paciente_id
        in: form
        type: integer
        required: true
        description: ID del paciente
      - name: descripcion
        in: form
        type: string
        required: true
        description: Descripción de la prestación
      - name: monto
        in: form
        type: number
        required: true
        description: Monto de la prestación
      - name: codigo_id
        in: form
        type: integer
        description: ID del código
      - name: observaciones
        in: form
        type: string
        description: Observaciones adicionales
    responses:
      200:
        description: Formulario para crear prestación (GET) o prestación creada (POST)
      302:
        description: Redirección después de crear prestación exitosamente
    """
    if request.method == 'POST':
        try:
            prestacion = PrestacionService.crear_prestacion({
                'paciente_id': request.form['paciente_id'],
                'descripcion': request.form['descripcion'],
                'monto': request.form['monto'],
                'codigo_id': request.form.get('codigo_id') if request.form.get('codigo_id') else None,
                'observaciones': request.form.get('observaciones'),
            })
            flash('Prestación registrada exitosamente', 'success')
            return redirect(url_for('main.listar_prestaciones'))
        except Exception as e:
            flash(f'Error al registrar prestación: {str(e)}', 'error')

    pacientes = PrestacionService.listar_pacientes()
    codigos = PrestacionService.listar_codigos()
    return render_template('prestaciones/nueva.html', pacientes=pacientes, codigos=codigos)
