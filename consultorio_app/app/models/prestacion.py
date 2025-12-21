from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db

class Prestacion(db.Model):
    __tablename__ = "prestaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    paciente = relationship("Paciente", back_populates="prestaciones")
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)
    observaciones = Column(String, nullable=True)
    turnos = relationship("Turno", back_populates="prestacion")
    practicas_assoc = relationship("PrestacionPractica", back_populates="prestacion")

    def get_codigos(self) -> list[str]:
        codigos = []
        if self.practicas_assoc:
            for pp in self.practicas_assoc:
                if pp.practica and pp.practica.codigo:
                    codigos.append(pp.practica.codigo)
        return codigos

    def get_codigo(self) -> str | None:
        codes = self.get_codigos()
        if not codes:
            return None
        return ", ".join(codes)

    def __str__(self):
        codigo_str = f" ({self.get_codigo()})" if self.get_codigo() else ""
        return f"{self.descripcion}{codigo_str} - ${self.monto} ({self.fecha.strftime('%d/%m/%Y')})"