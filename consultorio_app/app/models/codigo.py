from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class Codigo(db.Model):
    __tablename__ = "codigos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=False)
    
    # Relación uno a muchos con operaciones
    operaciones = relationship("Operacion", back_populates="codigo")

    def __str__(self):
        return f"{self.numero} - {self.descripcion}"
