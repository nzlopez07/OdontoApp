from app.database.session import DatabaseSession
from app.models import Codigo


class CodigoService:
    @staticmethod
    def listar_codigos():
        return Codigo.query.order_by(Codigo.numero).all()

    @staticmethod
    def crear_codigo(numero: str, descripcion: str = None):
        session = DatabaseSession.get_instance().session
        codigo = Codigo(numero=numero, descripcion=descripcion)
        session.add(codigo)
        session.commit()
        return codigo
