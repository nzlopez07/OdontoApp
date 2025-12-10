from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class Paciente(db.Model):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    dni = Column(String, nullable=False)
    fecha_nac = Column(Date, nullable=False)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    localidad_id = Column(Integer, ForeignKey("localidades.id"), nullable=True)
    localidad = relationship("Localidad", back_populates="pacientes")
    obra_social_id = Column(Integer, ForeignKey("obras_sociales.id"), nullable=True)
    obra_social = relationship("ObraSocial", back_populates="pacientes")
    carnet = Column(String, nullable=True)
    titular = Column(String, nullable=True)
    parentesco = Column(String, nullable=True)
    lugar_trabajo = Column(String, nullable=True)
    barrio = Column(String, nullable=True)
    turnos = relationship("Turno", back_populates="paciente", cascade="all, delete-orphan")
    operaciones = relationship("Operacion", back_populates="paciente")

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"

    def agendar_turno(self, turno):
        self.turnos.append(turno)

    def registrar_operacion(self, operacion):
        self.operaciones.append(operacion)
