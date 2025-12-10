from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.database import db

class Estado(db.Model):
    __tablename__ = 'estados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)

    cambios_estado = relationship("CambioEstado", back_populates="estado")
