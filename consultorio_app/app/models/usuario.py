"""
Modelo de Usuario para autenticación y control de acceso.

Roles disponibles:
- DUEÑA: Acceso completo a funcionalidad clínica + finanzas
- ODONTOLOGA: Acceso a funciones clínicas (sin finanzas)
- ADMIN: Acceso técnico/administración del sistema (logs, BD, backups)
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.database import db


class Usuario(UserMixin, db.Model):
    """Modelo de usuario del sistema con roles."""
    
    __tablename__ = 'usuarios'
    
    # Campos básicos
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Información personal
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    
    # Control de acceso
    rol = db.Column(db.String(20), nullable=False, default='ODONTOLOGA')  # DUEÑA | ODONTOLOGA | ADMIN
    activo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    fecha_modificacion = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Usuario {self.username} ({self.rol})>'
    
    # === Métodos de password ===
    
    def set_password(self, password: str):
        """Hashea y guarda la contraseña."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta."""
        return check_password_hash(self.password_hash, password)
    
    # === Métodos de Flask-Login (heredados de UserMixin) ===
    # get_id(), is_authenticated, is_active, is_anonymous
    
    @property
    def is_active(self):
        """Requerido por Flask-Login."""
        return self.activo
    
    # === Métodos de autorización ===
    
    def es_duena(self) -> bool:
        """Verifica si el usuario tiene rol de DUEÑA."""
        return self.rol == 'DUEÑA'
    
    def es_odontologa(self) -> bool:
        """Verifica si el usuario tiene rol de ODONTOLOGA."""
        return self.rol == 'ODONTOLOGA'
    
    def es_admin(self) -> bool:
        """Verifica si el usuario tiene rol de ADMIN (técnico)."""
        return self.rol == 'ADMIN'
    
    def tiene_acceso_clinico(self) -> bool:
        """Verifica si puede acceder a funciones clínicas (pacientes, turnos, odontogramas)."""
        return self.rol in ('DUEÑA', 'ODONTOLOGA')
    
    def tiene_acceso_finanzas(self) -> bool:
        """Verifica si puede acceder a información financiera (prestaciones, montos)."""
        return self.rol == 'DUEÑA'
    
    def tiene_acceso_admin(self) -> bool:
        """Verifica si puede acceder al panel de administración técnica (logs, BD)."""
        return self.rol == 'ADMIN'
    
    # === Métodos de utilidad ===
    
    @property
    def nombre_completo(self) -> str:
        """Retorna nombre y apellido."""
        return f"{self.nombre} {self.apellido}"
    
    def actualizar_ultimo_login(self):
        """Actualiza timestamp del último login."""
        self.ultimo_login = datetime.utcnow()
        db.session.commit()
