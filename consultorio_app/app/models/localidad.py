from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class Localidad(db.Model):
    __tablename__ = 'localidades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)

    pacientes = relationship("Paciente", back_populates="localidad")
