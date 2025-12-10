from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class Operacion(db.Model):
    __tablename__ = "operaciones"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    paciente = relationship("Paciente", back_populates="operaciones")
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)
    codigo_id = Column(Integer, ForeignKey("codigos.id"), nullable=True)
    codigo = relationship("Codigo", back_populates="operaciones")
    observaciones = Column(String, nullable=True)
    turnos = relationship("Turno", back_populates="operacion")

    def __str__(self):
        codigo_str = f" ({self.codigo.numero})" if self.codigo else ""
        return f"{self.descripcion}{codigo_str} - ${self.monto} ({self.fecha.strftime('%d/%m/%Y')})"
