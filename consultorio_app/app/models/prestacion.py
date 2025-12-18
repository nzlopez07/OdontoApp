from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db

class Prestacion(db.Model):
    __tablename__ = "prestaciones"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    paciente = relationship("Paciente", back_populates="prestaciones")
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)
    codigo_id = Column(Integer, ForeignKey("codigos.id"), nullable=True)
    codigo = relationship("Codigo", back_populates="prestaciones")
    observaciones = Column(String, nullable=True)
    turnos = relationship("Turno", back_populates="prestacion")

    def __str__(self):
        codigo_str = f" ({self.codigo.numero})" if self.codigo else ""
        return f"{self.descripcion}{codigo_str} - ${self.monto} ({self.fecha.strftime('%d/%m/%Y')})"