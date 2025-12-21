from datetime import date
from dateutil.relativedelta import relativedelta
from app.database.session import DatabaseSession
from app.models import Paciente, Localidad, ObraSocial, Prestacion, Turno
from app.services.busqueda_utils import BusquedaUtils


class PacienteService:
    @staticmethod
    def listar_pacientes(termino_busqueda: str | None = None):
        termino = (termino_busqueda or "").strip()
        if termino:
            return BusquedaUtils.buscar_pacientes_simple(termino)
        return Paciente.query.all()

    @staticmethod
    def crear_paciente(data: dict):
        session = DatabaseSession.get_instance().session
        paciente = Paciente(
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            dni=data.get('dni'),
            fecha_nac=data.get('fecha_nac'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            obra_social_id=data.get('obra_social_id'),
            localidad_id=data.get('localidad_id'),
            nro_afiliado=data.get('nro_afiliado'),
            titular=data.get('titular'),
            parentesco=data.get('parentesco'),
            lugar_trabajo=data.get('lugar_trabajo'),
            barrio=data.get('barrio'),
        )
        session.add(paciente)
        session.commit()
        return paciente

    @staticmethod
    def actualizar_paciente(paciente: Paciente, data: dict):
        session = DatabaseSession.get_instance().session
        for field in (
            'nombre', 'apellido', 'dni', 'fecha_nac', 'telefono', 'direccion',
            'obra_social_id', 'localidad_id', 'nro_afiliado', 'titular',
            'parentesco', 'lugar_trabajo', 'barrio'
        ):
            if field in data:
                setattr(paciente, field, data[field])
        session.commit()
        return paciente

    @staticmethod
    def obtener_paciente(id_: int):
        return Paciente.query.get(id_)

    @staticmethod
    def obtener_detalle(id_: int):
        paciente = Paciente.query.get(id_)
        if not paciente:
            return None, None, None, None, None

        turnos_q = Turno.query.filter_by(paciente_id=id_).order_by(Turno.fecha.desc(), Turno.hora.desc())
        prestaciones_q = Prestacion.query.filter_by(paciente_id=id_).order_by(Prestacion.fecha.desc())

        turnos = turnos_q.limit(5).all()
        prestaciones = prestaciones_q.limit(5).all()

        totales = {
            'turnos': turnos_q.count(),
            'prestaciones': prestaciones_q.count(),
        }

        edad = None
        if paciente.fecha_nac:
            edad = relativedelta(date.today(), paciente.fecha_nac).years

        return paciente, turnos, prestaciones, edad, totales

    @staticmethod
    def listar_obras_sociales():
        return ObraSocial.query.order_by(ObraSocial.nombre).all()

    @staticmethod
    def listar_localidades():
        return Localidad.query.order_by(Localidad.nombre).all()
