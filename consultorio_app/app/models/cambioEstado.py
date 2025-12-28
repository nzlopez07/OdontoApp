from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import db

class CambioEstado(db.Model):
    __tablename__ = 'cambios_estado'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    turno_id = Column(Integer, ForeignKey('turnos.id'), nullable=False)
    # Legacy strings
    estado_anterior = Column(String, nullable=True)
    estado_nuevo = Column(String, nullable=False)
    # Nuevos FKs hacia estados
    estado_anterior_id = Column(Integer, ForeignKey('estados.id'), nullable=True)
    estado_nuevo_id = Column(Integer, ForeignKey('estados.id'), nullable=True)
    
    fecha_cambio = Column(DateTime, default=datetime.now, nullable=False)
    motivo = Column(String, nullable=True)  # Motivo del cambio

    turno = relationship("Turno", back_populates="cambios_estado")
    estado_anterior_ref = relationship('Estado', foreign_keys=[estado_anterior_id])
    estado_nuevo_ref = relationship('Estado', foreign_keys=[estado_nuevo_id])
    
    def __str__(self):
        return f"{self.estado_anterior} → {self.estado_nuevo} ({self.fecha_cambio.strftime('%d/%m/%Y %H:%M')})"
