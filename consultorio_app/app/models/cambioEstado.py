from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class CambioEstado(db.Model):
    __tablename__ = 'cambios_estado'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    turno_id = Column(Integer, ForeignKey('turnos.id'), nullable=False)
    estado_id = Column(Integer, ForeignKey('estados.id'), nullable=False)
    
    inicio_estado = Column(DateTime, default=datetime.now(), nullable=False)
    fin_estado = Column(DateTime, nullable=True)  # null implica estado actual

    turno = relationship("Turno", back_populates="cambios_estado")
    estado = relationship("Estado", back_populates="cambios_estado")
