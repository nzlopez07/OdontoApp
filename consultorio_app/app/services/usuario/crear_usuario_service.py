"""
Servicio para crear usuarios en el sistema.
"""

from app.database import db
from app.models import Usuario


class CrearUsuarioService:
    """Servicio para crear nuevos usuarios."""
    
    @staticmethod
    def execute(
        username: str,
        email: str,
        password: str,
        nombre: str,
        apellido: str,
        rol: str = 'ODONTOLOGA'
    ) -> Usuario:
        """
        Crea un nuevo usuario en el sistema.
        
        Args:
            username: Nombre de usuario único
            email: Email único
            password: Contraseña en texto plano (se hasheará)
            nombre: Nombre del usuario
            apellido: Apellido del usuario
            rol: Rol del usuario (DUEÑA | ODONTOLOGA | ADMIN)
        
        Returns:
            Usuario creado
        
        Raises:
            ValueError: Si username o email ya existe, o rol inválido
        """
        # Validar rol
        if rol not in ('DUEÑA', 'ODONTOLOGA', 'ADMIN'):
            raise ValueError(f"Rol inválido: {rol}. Debe ser 'DUEÑA', 'ODONTOLOGA' o 'ADMIN'")
        
        # Verificar username único
        if Usuario.query.filter_by(username=username).first():
            raise ValueError(f"El username '{username}' ya existe")
        
        # Verificar email único
        if Usuario.query.filter_by(email=email).first():
            raise ValueError(f"El email '{email}' ya está registrado")
        
        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            nombre=nombre,
            apellido=apellido,
            rol=rol,
            activo=True
        )
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        return usuario
