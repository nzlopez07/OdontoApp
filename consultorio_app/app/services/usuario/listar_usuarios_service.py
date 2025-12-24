"""
Servicio para listar usuarios del sistema.
"""

from typing import List
from app.models import Usuario


class ListarUsuariosService:
    """Servicio para listar usuarios."""
    
    @staticmethod
    def listar_todos() -> List[Usuario]:
        """Retorna todos los usuarios del sistema."""
        return Usuario.query.order_by(Usuario.username).all()
    
    @staticmethod
    def listar_activos() -> List[Usuario]:
        """Retorna solo usuarios activos."""
        return Usuario.query.filter_by(activo=True).order_by(Usuario.username).all()
    
    @staticmethod
    def listar_por_rol(rol: str) -> List[Usuario]:
        """Retorna usuarios de un rol específico."""
        return Usuario.query.filter_by(rol=rol, activo=True).order_by(Usuario.username).all()
