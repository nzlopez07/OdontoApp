from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import db

class Codigo(db.Model):
    __tablename__ = "codigos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=False)
    
    # Relación uno a muchos con prestaciones
    prestaciones = relationship("Prestacion", back_populates="codigo")

    def __str__(self):
        return f"{self.numero} - {self.descripcion}"
