from app.database.session import DatabaseSession
from app.models import Localidad


class LocalidadService:
    @staticmethod
    def listar_localidades():
        return Localidad.query.order_by(Localidad.nombre).all()

    @staticmethod
    def crear_localidad(nombre: str):
        session = DatabaseSession.get_instance().session
        loc = Localidad(nombre=nombre)
        session.add(loc)
        session.commit()
        return loc
