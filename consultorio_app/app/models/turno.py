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
    detalle = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    cambios_estado = relationship("CambioEstado", back_populates="turno", cascade="all, delete-orphan")
    prestacion_id = Column(Integer, ForeignKey("prestaciones.id"), nullable=True)
    prestacion = relationship("Prestacion", back_populates="turnos")

    def __str__(self):
        return f"Turno {self.id} - {self.fecha} {self.hora} - {self.estado or 'Pendiente'}"
