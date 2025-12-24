from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_user_id = Column(String, unique=True, nullable=False, index=True)
    paso_actual = Column(String, nullable=False, default="solicitar_dni")

    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    paciente = relationship("Paciente")

    dni_propuesto = Column(String, nullable=True)
    nombre_tmp = Column(String, nullable=True)
    apellido_tmp = Column(String, nullable=True)
    telefono_tmp = Column(String, nullable=True)

    fecha_candidate = Column(Date, nullable=True)
    hora_candidate = Column(Time, nullable=True)
    duracion_candidate = Column(Integer, nullable=True)
    detalle = Column(String, nullable=True)

    expira_en = Column(DateTime, nullable=True)
    ultima_interaccion_ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    intentos_actuales = Column(Integer, default=0, nullable=False)
    confirmed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
