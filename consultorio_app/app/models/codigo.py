from sqlalchemy import Column, Integer, String
from app.database import db

class Codigo(db.Model):
    __tablename__ = "codigos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=False)

    def __str__(self):
        return f"{self.numero} - {self.descripcion}"

    @property
    def codigo(self) -> str:
        return self.numero
