import os
import json
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app
from flask_login import login_required
from app.models import Prestacion, ObraSocial, Localidad
from app.services.paciente import (
    BuscarPacientesService,
    CrearPacienteService,
    EditarPacienteService,
)
from app.services.odontograma import (
  ObtenerOdontogramaService,
  CrearVersionOdontogramaService,
)
from app.services.common import (
    PacienteNoEncontradoError,
    PacienteDuplicadoError,
    DatosInvalidosPacienteError,
    LocalidadNoEncontradaError,
    PacienteError,
)
from . import main_bp


@main_bp.route('/media/<path:filename>')
@login_required
def media_file(filename: str):
  """Sirve archivos estáticos ubicados en app/media (imagen y hoja del odontograma)."""
  media_dir = os.path.join(current_app.root_path, 'media')
  return send_from_directory(media_dir, filename)


@main_bp.route('/odontograma/slots', methods=['POST'])
@login_required
def guardar_slots_odontograma():
  """Guarda la configuración de slots calibrados para el odontograma."""
  data = request.get_json(silent=True) or {}
  if 'config' not in data or 'teeth' not in data:
    return jsonify({"error": "Payload inválido"}), 400
  slots_path = os.path.join(current_app.root_path, 'media', 'odontograma_slots.json')
  try:
    with open(slots_path, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
  except Exception:
    return jsonify({"error": "No se pudo guardar la calibración"}), 500


@main_bp.route('/pacientes')
@login_required
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
    pacientes = BuscarPacientesService.buscar(termino_busqueda)
    return render_template(
      'pacientes/lista.html',
      pacientes=pacientes,
      termino_busqueda=termino_busqueda,
    )


@main_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
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
    obras_sociales = ObraSocial.query.order_by(ObraSocial.nombre).all()
    localidades = Localidad.query.order_by(Localidad.nombre).all()

    if request.method == 'POST':
        try:
            fecha_nac = datetime.strptime(request.form['fecha_nac'], '%Y-%m-%d').date() if request.form.get('fecha_nac') else None
            localidad_nombre = request.form.get('localidad_nombre', '').strip() or None

            CrearPacienteService.execute(
              nombre=request.form['nombre'],
              apellido=request.form['apellido'],
              dni=request.form['dni'],
              fecha_nac=fecha_nac,
              telefono=request.form.get('telefono'),
              direccion=request.form.get('direccion'),
              barrio=request.form.get('barrio'),
              localidad_nombre=localidad_nombre,
              localidad_id=int(request.form['localidad_id']) if request.form.get('localidad_id') else None,
              obra_social_id=int(request.form['obra_social_id']) if request.form.get('obra_social_id') else None,
              nro_afiliado=request.form.get('carnet'),
              titular=request.form.get('titular'),
              parentesco=request.form.get('parentesco'),
              lugar_trabajo=request.form.get('lugar_trabajo'),
            )
            flash('Paciente creado exitosamente', 'success')
            return redirect(url_for('main.listar_pacientes'))
        except (DatosInvalidosPacienteError, PacienteDuplicadoError, LocalidadNoEncontradaError) as e:
            flash(str(e), 'error')
        except PacienteError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear paciente: {str(e)}', 'error')

    return render_template(
        'pacientes/formulario.html',
        obras_sociales=obras_sociales,
        localidades=localidades,
    )


@main_bp.route('/pacientes/<int:id>')
@login_required
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
    try:
        detalle = BuscarPacientesService.obtener_detalle_completo(id)
    except PacienteNoEncontradoError:
        return redirect(url_for('main.listar_pacientes'))

    paciente = detalle['paciente']
    turnos = detalle['turnos']
    prestaciones = detalle['prestaciones']
    edad = detalle.get('edad')
    estadisticas = {
      'total_turnos': detalle.get('total_turnos', 0),
      'total_prestaciones': detalle.get('total_prestaciones', 0),
    }

    # Obtener estado del odontograma (si está desactualizado)
    odontograma, _, desactualizado_odonto, ultima_prestacion = ObtenerOdontogramaService.obtener_actual(id)
    
    # Marcar prestaciones posteriores al odontograma
    prestaciones_nuevas = set()
    if desactualizado_odonto and odontograma.creado_en:
        for p in prestaciones:
            if p and p.fecha:
                # Convertir ambos a datetime para comparación
                prestacion_dt = p.fecha if hasattr(p.fecha, 'hour') else datetime.combine(p.fecha, datetime.min.time())
                if prestacion_dt > odontograma.creado_en:
                    prestaciones_nuevas.add(p.id)

    return render_template(
        'pacientes/detalle.html',
        paciente=paciente,
        edad=edad,
        turnos=turnos,
        prestaciones=prestaciones,
        estadisticas=estadisticas,
        desactualizado_odonto=desactualizado_odonto,
        prestaciones_nuevas=prestaciones_nuevas,
    )



@main_bp.route('/pacientes/<int:id>/odontograma')
@login_required
def ver_odontograma_paciente(id: int):
    """Vista del odontograma versionado de un paciente.
    Si no existe odontograma, crea uno vacío como versión actual.
    Permite navegar versiones vía query param odontograma_id.
    """
    try:
        odontograma_id = request.args.get('odontograma_id', type=int)

        if odontograma_id:
            odontograma, versiones, desactualizado, ultima_prestacion = ObtenerOdontogramaService.obtener_version(
                paciente_id=id, odontograma_id=odontograma_id
            )
            if not odontograma:
                flash('Odontograma no encontrado para este paciente', 'error')
                return redirect(url_for('main.ver_paciente', id=id))
        else:
            odontograma, versiones, desactualizado, ultima_prestacion = ObtenerOdontogramaService.obtener_actual(id)

        return render_template(
            'pacientes/odontograma.html',
            odontograma=odontograma,
            versiones=versiones,
            desactualizado=desactualizado,
            ultima_prestacion=ultima_prestacion,
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.ver_paciente', id=id))


@main_bp.route('/pacientes/<int:id>/odontograma/datos')
@login_required
def obtener_datos_odontograma(id: int):
    """Devuelve en JSON la versión del odontograma solicitada o la actual."""
    try:
        odontograma_id = request.args.get('odontograma_id', type=int)
        if odontograma_id:
            odontograma, versiones, desactualizado, ultima_prestacion = ObtenerOdontogramaService.obtener_version(
                paciente_id=id, odontograma_id=odontograma_id
            )
            if not odontograma:
                return jsonify({"error": "Odontograma no encontrado"}), 404
        else:
            odontograma, versiones, desactualizado, ultima_prestacion = ObtenerOdontogramaService.obtener_actual(id)

        def _serializar_odontograma(od):
          return {
            "id": od.id,
            "paciente_id": od.paciente_id,
            "version_seq": od.version_seq,
            "es_actual": od.es_actual,
            "nota_general": od.nota_general,
            "ultima_prestacion_registrada_en": od.ultima_prestacion_registrada_en.isoformat() if od.ultima_prestacion_registrada_en else None,
            "creado_en": od.creado_en.isoformat() if od.creado_en else None,
            "actualizado_en": od.actualizado_en.isoformat() if od.actualizado_en else None,
            "caras": [
              {
                "id": c.id,
                "diente": getattr(c, 'diente', None),
                "cara": getattr(c, 'cara', None),
                "marca_codigo": getattr(c, 'marca_codigo', None),
                "marca_texto": getattr(c, 'marca_texto', None),
                "comentario": getattr(c, 'comentario', None),
              }
              for c in getattr(od, 'caras', [])
            ]
          }

        return jsonify({
            "odontograma": _serializar_odontograma(odontograma),
            "versiones": [
                {
                    "id": v.id,
                    "version_seq": v.version_seq,
                    "es_actual": v.es_actual,
                    "nota_general": v.nota_general,
                    "actualizado_en": v.actualizado_en.isoformat() if v.actualizado_en else None,
                }
                for v in versiones
            ],
            "desactualizado": desactualizado,
            "ultima_prestacion": ultima_prestacion.isoformat() if ultima_prestacion else None,
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@main_bp.route('/pacientes/<int:id>/odontograma/version', methods=['POST'])
@login_required
def crear_version_odontograma(id: int):
    """Crea una nueva versión de odontograma aplicando cambios de caras."""
    data = request.get_json(silent=True) or {}
    cambios = data.get('caras') or []
    nota_general = data.get('nota_general')
    base_id = data.get('odontograma_base_id')

    try:
        nuevo, versiones = CrearVersionOdontogramaService.execute(
            paciente_id=id,
            cambios_caras=cambios,
            nota_general=nota_general,
            base_odontograma_id=base_id,
        )

        # Consultar última prestación para marcar desactualización
        _, _, _, ultima_prestacion = ObtenerOdontogramaService.obtener_actual(id)
        desactualizado = False
        if ultima_prestacion and (
            not nuevo.ultima_prestacion_registrada_en
            or ultima_prestacion > nuevo.ultima_prestacion_registrada_en
        ):
            desactualizado = True

        def _serializar_odontograma(od):
            return {
                "id": od.id,
                "paciente_id": od.paciente_id,
                "version_seq": od.version_seq,
                "es_actual": od.es_actual,
                "nota_general": od.nota_general,
                "ultima_prestacion_registrada_en": od.ultima_prestacion_registrada_en.isoformat() if od.ultima_prestacion_registrada_en else None,
                "creado_en": od.creado_en.isoformat() if od.creado_en else None,
                "actualizado_en": od.actualizado_en.isoformat() if od.actualizado_en else None,
                "caras": [
                    {
                        "id": c.id,
                        "diente": getattr(c, 'diente', None),
                        "cara": getattr(c, 'cara', None),
                        "marca_codigo": getattr(c, 'marca_codigo', None),
                        "marca_texto": getattr(c, 'marca_texto', None),
                        "comentario": getattr(c, 'comentario', None),
                    }
                    for c in getattr(od, 'caras', [])
                ]
            }

        return jsonify({
            "odontograma": _serializar_odontograma(nuevo),
            "versiones": [
                {
                    "id": v.id,
                    "version_seq": v.version_seq,
                    "es_actual": v.es_actual,
                    "nota_general": v.nota_general,
                    "actualizado_en": v.actualizado_en.isoformat() if v.actualizado_en else None,
                }
                for v in versiones
            ],
            "desactualizado": desactualizado,
            "ultima_prestacion": ultima_prestacion.isoformat() if ultima_prestacion else None,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "No se pudo crear la nueva versión"}), 500


@main_bp.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_paciente(id: int):
    """Editar un paciente existente."""
    try:
        paciente = BuscarPacientesService.obtener_por_id(id)
    except PacienteNoEncontradoError:
        return redirect(url_for('main.listar_pacientes'))

    if request.method == 'POST':
        try:
            fecha_nac = datetime.strptime(request.form['fecha_nac'], '%Y-%m-%d').date() if request.form.get('fecha_nac') else None
            localidad_nombre = request.form.get('localidad_nombre', '').strip() or None

            EditarPacienteService.execute(
                paciente_id=paciente.id,
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form['dni'],
                fecha_nac=fecha_nac,
                telefono=request.form.get('telefono'),
                direccion=request.form.get('direccion'),
                barrio=request.form.get('barrio'),
                localidad_nombre=localidad_nombre,
                localidad_id=int(request.form['localidad_id']) if request.form.get('localidad_id') else None,
                obra_social_id=int(request.form['obra_social_id']) if request.form.get('obra_social_id') else None,
                nro_afiliado=request.form.get('carnet'),
                titular=request.form.get('titular'),
                parentesco=request.form.get('parentesco'),
                lugar_trabajo=request.form.get('lugar_trabajo'),
            )
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=paciente.id))
        except (DatosInvalidosPacienteError, PacienteDuplicadoError, LocalidadNoEncontradaError) as e:
            flash(str(e), 'error')
        except PacienteError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar paciente: {str(e)}', 'error')

    obras_sociales = ObraSocial.query.order_by(ObraSocial.nombre).all()
    localidades = Localidad.query.order_by(Localidad.nombre).all()

    return render_template(
        'pacientes/formulario.html',
        paciente=paciente,
        obras_sociales=obras_sociales,
        localidades=localidades,
    )
