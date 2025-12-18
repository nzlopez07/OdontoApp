from app.database.session import DatabaseSession
from app.models import Estado


class EstadoService:
    @staticmethod
    def listar_estados():
        return Estado.query.order_by(Estado.nombre).all()

    @staticmethod
    def asegurar_estados_por_defecto(nombres):
        session = DatabaseSession.get_instance().session
        for nombre in nombres:
            if not Estado.query.filter_by(nombre=nombre).first():
                session.add(Estado(nombre=nombre))
        session.commit()
