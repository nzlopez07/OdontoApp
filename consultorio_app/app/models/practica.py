from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import db

class Practica(db.Model):
    __tablename__ = "practicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(30), nullable=False)
    descripcion = Column(String(200), nullable=False)
    proveedor_tipo = Column(String(20), nullable=False)
    obra_social_id = Column(Integer, ForeignKey("obras_sociales.id"), nullable=True)
    monto_unitario = Column(Float, nullable=False, default=0.0)

    obra_social = relationship("ObraSocial", back_populates="practicas", foreign_keys=[obra_social_id])
    prestaciones_assoc = relationship("PrestacionPractica", back_populates="practica")

    __table_args__ = (
        UniqueConstraint('proveedor_tipo', 'obra_social_id', 'codigo', name='uq_practica_codigo_por_proveedor'),
    )

    def __str__(self):
        proveedor = self.proveedor_tipo + (f"/{self.obra_social.nombre}" if self.obra_social else "")
        return f"[{proveedor}] {self.codigo} - {self.descripcion}"
