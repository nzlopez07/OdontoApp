from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db

class Turno(db.Model):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    paciente = relationship("Paciente", back_populates="turnos")
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    duracion = Column(Integer, default=30, nullable=False)  # Duración en minutos (default 30)
    detalle = Column(String, nullable=True)
    # Estado legacy como string (se mantiene por compatibilidad)
    estado = Column(String, nullable=True)
    # Nuevo: FK hacia tabla estados (nullable para migración gradual)
    estado_id = Column(Integer, ForeignKey('estados.id'), nullable=True)
    # Relación opcional para acceso al objeto Estado
    estado_obj = relationship('Estado')
    cambios_estado = relationship("CambioEstado", back_populates="turno", cascade="all, delete-orphan")
    prestacion_id = Column(Integer, ForeignKey("prestaciones.id"), nullable=True)
    prestacion = relationship("Prestacion", back_populates="turnos")

    def __str__(self):
        return f"Turno {self.id} - {self.fecha} {self.hora} ({self.duracion}min) - {self.estado or 'Pendiente'}"

    @property
    def estado_nombre(self):
        """Nombre del estado usando FK; fallback al string legacy o 'Pendiente'."""
        if self.estado_obj and getattr(self.estado_obj, 'nombre', None):
            return self.estado_obj.nombre
        return self.estado or 'Pendiente'
