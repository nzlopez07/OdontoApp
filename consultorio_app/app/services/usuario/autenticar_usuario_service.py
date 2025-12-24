"""
Servicio para autenticar usuarios.
"""

from typing import Optional
from app.models import Usuario


class AutenticarUsuarioService:
    """Servicio para autenticar usuarios."""
    
    @staticmethod
    def execute(username: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario con username y password.
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña en texto plano
        
        Returns:
            Usuario si las credenciales son correctas, None si no
        """
        # Buscar por username o email
        usuario = Usuario.query.filter(
            (Usuario.username == username) | (Usuario.email == username)
        ).first()
        
        if not usuario:
            return None
        
        if not usuario.activo:
            return None
        
        if not usuario.check_password(password):
            return None
        
        # Actualizar último login
        usuario.actualizar_ultimo_login()
        
        return usuario
