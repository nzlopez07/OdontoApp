from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
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
    cambios_estado = relationship("CambioEstado", back_populates="turno")
    operacion_id = Column(Integer, ForeignKey("operaciones.id"), nullable=True)
    operacion = relationship("Operacion", back_populates="turnos")

    def registrar_cambio_estado(self, nuevo_estado, usuario=None):
        # Import local para evitar import circular
        from app.models.cambioEstado import CambioEstado
        
        # Cierra el anterior si lo hay
        for cambio in self.cambios_estado:
            if cambio.es_estado_actual():
                cambio.cerrar()
        # Agrega nuevo
        nuevo = CambioEstado(
            id=len(self.cambios_estado) + 1,
            turno_id=self.id,
            estado=nuevo_estado,
            usuario=usuario
        )
        self.cambios_estado.append(nuevo)
        self.estado = nuevo_estado

    def estado_actual(self):
        for cambio in reversed(self.cambios_estado):
            if cambio.es_estado_actual():
                return cambio.estado
        return None

    def __str__(self):
        return f"Turno {self.id} - {self.fecha} {self.hora} - {self.estado_actual()}"
