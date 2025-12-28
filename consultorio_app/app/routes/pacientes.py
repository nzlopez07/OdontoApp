import os
import json
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app
from flask_login import login_required
from app.models import Prestacion, ObraSocial, Localidad, Paciente
from app.forms import PacienteForm
from app.services.paciente import (
    BuscarPacientesService,
    CrearPacienteService,
    EditarPacienteService,
    EliminarPacienteService,
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
    """Crear un nuevo paciente con validación formal WTF."""
    form = PacienteForm()
    
    # Poblar select fields dinámicamente (DESPUÉS de instanciar)
    form.localidad_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(loc.id, loc.nombre) for loc in Localidad.query.order_by(Localidad.nombre).all()]
    ]
    form.obra_social_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(os.id, os.nombre) for os in ObraSocial.query.order_by(ObraSocial.nombre).all()]
    ]
    
    if form.validate_on_submit():
        try:
            # Los datos ya están validados por WTF
            CrearPacienteService.execute(
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                dni=form.dni.data,
                fecha_nac=form.fecha_nac.data,
                telefono=form.telefono.data or None,
                lugar_trabajo=form.lugar_trabajo.data or None,
                direccion=form.direccion.data or None,
                barrio=form.barrio.data or None,
                localidad_id=form.localidad_id.data if form.localidad_id.data and form.localidad_id.data != 0 else None,
                obra_social_id=form.obra_social_id.data if form.obra_social_id.data and form.obra_social_id.data != 0 else None,
                nro_afiliado=form.nro_afiliado.data or None,
                titular=form.titular.data or None,
                parentesco=form.parentesco.data or None,
            )
            flash('Paciente creado exitosamente', 'success')
            return redirect(url_for('main.listar_pacientes'))
        except (DatosInvalidosPacienteError, PacienteDuplicadoError, LocalidadNoEncontradaError) as e:
            flash(str(e), 'error')
        except PacienteError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear paciente: {str(e)}', 'error')

    return render_template('pacientes/formulario.html', form=form)


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


@main_bp.route('/pacientes/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_paciente(id: int):
    """Elimina un paciente y sus datos relacionados (turnos, odontogramas)."""
    try:
        resultado = EliminarPacienteService.execute(id)
        flash(resultado['mensaje'], 'success')
    except PacienteNoEncontradoError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al eliminar paciente: {str(e)}', 'error')

    return redirect(url_for('main.listar_pacientes'))


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
    except Exception as e:
        import traceback
        traceback.print_exc()  # Esto imprimirá el error en la consola
        return jsonify({"error": f"No se pudo crear la nueva versión: {str(e)}"}), 500


@main_bp.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_paciente(id: int):
    """Editar un paciente existente con validación WTF."""
    try:
        paciente = BuscarPacientesService.obtener_por_id(id)
    except PacienteNoEncontradoError:
        return redirect(url_for('main.listar_pacientes'))

    form = PacienteForm()
    
    # Poblar select fields dinámicamente
    form.localidad_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(loc.id, loc.nombre) for loc in Localidad.query.order_by(Localidad.nombre).all()]
    ]
    form.obra_social_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(os.id, os.nombre) for os in ObraSocial.query.order_by(ObraSocial.nombre).all()]
    ]
    
    # Pre-poblar formulario en GET
    if request.method == 'GET':
        form.nombre.data = paciente.nombre
        form.apellido.data = paciente.apellido
        form.dni.data = paciente.dni
        form.fecha_nac.data = paciente.fecha_nac
        form.telefono.data = paciente.telefono
        form.lugar_trabajo.data = paciente.lugar_trabajo if hasattr(paciente, 'lugar_trabajo') else None
        form.direccion.data = paciente.direccion
        form.barrio.data = paciente.barrio if hasattr(paciente, 'barrio') else None
        form.localidad_id.data = paciente.localidad_id if paciente.localidad_id else 0
        form.obra_social_id.data = paciente.obra_social_id if paciente.obra_social_id else 0
        form.nro_afiliado.data = paciente.nro_afiliado
        form.titular.data = paciente.titular if hasattr(paciente, 'titular') else None
        form.parentesco.data = paciente.parentesco if hasattr(paciente, 'parentesco') else None
    
    if form.validate_on_submit():
        try:
            # Los datos ya están validados por WTF
            EditarPacienteService.execute(
                paciente_id=paciente.id,
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                dni=form.dni.data,
                fecha_nac=form.fecha_nac.data,
                telefono=form.telefono.data or None,
                lugar_trabajo=form.lugar_trabajo.data or None,
                direccion=form.direccion.data or None,
                barrio=form.barrio.data or None,
                localidad_id=form.localidad_id.data if form.localidad_id.data and form.localidad_id.data != 0 else None,
                obra_social_id=form.obra_social_id.data if form.obra_social_id.data and form.obra_social_id.data != 0 else None,
                nro_afiliado=form.nro_afiliado.data or None,
                titular=form.titular.data or None,
                parentesco=form.parentesco.data or None,
            )
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('main.ver_paciente', id=paciente.id))
        except (DatosInvalidosPacienteError, PacienteDuplicadoError, LocalidadNoEncontradaError) as e:
            flash(str(e), 'error')
        except PacienteError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar paciente: {str(e)}', 'error')

    return render_template('pacientes/formulario.html', form=form, paciente=paciente)
