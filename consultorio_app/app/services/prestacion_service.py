from datetime import datetime
from app.database.session import DatabaseSession
from app.models import Prestacion, Paciente, Codigo


class PrestacionService:
    @staticmethod
    def listar_prestaciones():
        return Prestacion.query.order_by(Prestacion.fecha.desc()).all()

    @staticmethod
    def crear_prestacion(data: dict):
        session = DatabaseSession.get_instance().session
        prestacion = Prestacion(
            paciente_id=data.get('paciente_id'),
            descripcion=data.get('descripcion'),
            monto=float(data.get('monto')) if data.get('monto') is not None else 0,
            fecha=datetime.now(),
            codigo_id=data.get('codigo_id'),
            observaciones=data.get('observaciones'),
        )
        session.add(prestacion)
        session.commit()
        return prestacion

    @staticmethod
    def listar_pacientes():
        return Paciente.query.all()

    @staticmethod
    def listar_codigos():
        return Codigo.query.all()
