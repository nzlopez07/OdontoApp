from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class ObraSocial(db.Model):
    __tablename__ = 'obras_sociales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    codigo = Column(String(20), nullable=True)  # Para un identificador externo si lo tenés

    pacientes = relationship("Paciente", back_populates="obra_social")
