from app.database.session import DatabaseSession
from app.models import ObraSocial


class ObraSocialService:
    @staticmethod
    def listar_obras_sociales():
        return ObraSocial.query.order_by(ObraSocial.nombre).all()

    @staticmethod
    def crear_obra_social(nombre: str):
        session = DatabaseSession.get_instance().session
        obra = ObraSocial(nombre=nombre)
        session.add(obra)
        session.commit()
        return obra
