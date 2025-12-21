from app.database.session import DatabaseSession
from app.models import Practica, ObraSocial

class PracticaService:
    @staticmethod
    def listar_por_proveedor(obra_social_id: int | None = None):
        if obra_social_id:
            return Practica.query.filter_by(proveedor_tipo='OBRA_SOCIAL', obra_social_id=obra_social_id).all()
        return Practica.query.filter_by(proveedor_tipo='PARTICULAR').all()

    @staticmethod
    def buscar(termino: str, obra_social_id: int | None = None):
        q = Practica.query
        if obra_social_id:
            q = q.filter_by(proveedor_tipo='OBRA_SOCIAL', obra_social_id=obra_social_id)
        else:
            q = q.filter_by(proveedor_tipo='PARTICULAR')
        like = f"%{termino}%"
        return q.filter((Practica.codigo.ilike(like)) | (Practica.descripcion.ilike(like))).all()

    @staticmethod
    def crear_practica(data: dict):
        session = DatabaseSession.get_instance().session
        p = Practica(
            codigo=data['codigo'],
            descripcion=data['descripcion'],
            proveedor_tipo=data.get('proveedor_tipo', 'PARTICULAR'),
            obra_social_id=data.get('obra_social_id'),
            monto_unitario=float(data.get('monto_unitario', 0.0))
        )
        session.add(p)
        session.commit()
        return p

    @staticmethod
    def obtener_practica(practica_id: int):
        return Practica.query.get(practica_id)

    @staticmethod
    def actualizar_practica(practica_id: int, data: dict):
        session = DatabaseSession.get_instance().session
        p = session.query(Practica).get(practica_id)
        if not p:
            return None
        p.codigo = data.get('codigo', p.codigo)
        p.descripcion = data.get('descripcion', p.descripcion)
        p.proveedor_tipo = data.get('proveedor_tipo', p.proveedor_tipo)
        p.obra_social_id = data.get('obra_social_id', p.obra_social_id)
        if 'monto_unitario' in data:
            p.monto_unitario = float(data['monto_unitario'])
        session.commit()
        return p

    @staticmethod
    def eliminar_practica(practica_id: int):
        session = DatabaseSession.get_instance().session
        p = session.query(Practica).get(practica_id)
        if not p:
            return False
        session.delete(p)
        session.commit()
        return True
