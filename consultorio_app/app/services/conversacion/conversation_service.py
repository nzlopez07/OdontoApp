from datetime import datetime, timedelta
from typing import Optional
from app.database.session import DatabaseSession
from app.models import Conversation, Paciente
from app.services.paciente import CrearPacienteService, BuscarPacientesService
from app.services.turno import AgendarTurnoService
from app.services.common import PacienteDuplicadoError, DatosInvalidosPacienteError, PacienteNoEncontradoError, TurnoError


class ConversationReply:
    def __init__(self, message: str, step: str, done: bool = False):
        self.message = message
        self.step = step
        self.done = done

    def to_dict(self):
        return {"message": self.message, "step": self.step, "done": self.done}


class ConversationService:
    EXPIRATION_MINUTES = 30

    @staticmethod
    def _get_session():
        return DatabaseSession.get_instance().session

    @staticmethod
    def _get_or_create(channel_user_id: str) -> Conversation:
        import logging
        logger = logging.getLogger(__name__)
        
        session = ConversationService._get_session()
        convo = session.query(Conversation).filter_by(channel_user_id=channel_user_id).first()
        if convo:
            logger.debug(f"[_get_or_create] Found existing: id={convo.id}, paso={convo.paso_actual}, nombre={convo.nombre_tmp}")
            return convo
        
        logger.debug(f"[_get_or_create] Creating new conversation for {channel_user_id}")
        now = datetime.utcnow()
        convo = Conversation(
            channel_user_id=channel_user_id,
            paso_actual="solicitar_dni",
            expira_en=now + timedelta(minutes=ConversationService.EXPIRATION_MINUTES),
            ultima_interaccion_ts=now,
        )
        session.add(convo)
        session.commit()
        logger.debug(f"[_get_or_create] Created: id={convo.id}, paso={convo.paso_actual}")
        return convo

    @staticmethod
    def handle_message(channel_user_id: str, text: str) -> ConversationReply:
        session = ConversationService._get_session()
        convo = ConversationService._get_or_create(channel_user_id)
        
        # Debug log
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"[handle_message] User: {channel_user_id}, Text: {text}, Step: {convo.paso_actual}, nombre_tmp: {convo.nombre_tmp}")
        
        now = datetime.utcnow()
        convo.ultima_interaccion_ts = now
        convo.expira_en = now + timedelta(minutes=ConversationService.EXPIRATION_MINUTES)

        step = convo.paso_actual
        message = text.strip() if text else ""

        try:
            if step == "solicitar_dni":
                digits = "".join([c for c in message if c.isdigit()])
                if len(digits) < 6:
                    session.commit()
                    return ConversationReply("Necesito el DNI para continuar (6+ dígitos).", step)
                convo.dni_propuesto = digits
                # Buscar paciente
                paciente = session.query(Paciente).filter_by(dni=digits).first()
                if paciente:
                    convo.paciente_id = paciente.id
                    convo.paso_actual = "solicitar_fecha"
                    session.commit()
                    return ConversationReply("Encontré tu ficha. Indicá la fecha (YYYY-MM-DD).", convo.paso_actual)
                else:
                    convo.paso_actual = "solicitar_nombre"
                    session.commit()
                    return ConversationReply("No encontré tu ficha. Decime tu nombre para registrarte.", convo.paso_actual)

            if step == "solicitar_nombre":
                if not message:
                    session.commit()
                    return ConversationReply("Necesito tu nombre.", step)
                logger.debug(f"[solicitar_nombre] Guardando nombre_tmp='{message}'")
                convo.nombre_tmp = message
                convo.paso_actual = "solicitar_apellido"
                session.commit()
                logger.debug(f"[solicitar_nombre] Después de commit: nombre_tmp={convo.nombre_tmp}, paso={convo.paso_actual}")
                return ConversationReply("Gracias. Ahora tu apellido.", convo.paso_actual)

            if step == "solicitar_apellido":
                if not message:
                    session.commit()
                    return ConversationReply("Necesito tu apellido.", step)
                logger.debug(f"[solicitar_apellido] ANTES de guardar: nombre_tmp={convo.nombre_tmp}, apellido_tmp={convo.apellido_tmp}")
                convo.apellido_tmp = message
                logger.debug(f"[solicitar_apellido] Guardando apellido_tmp='{message}', nombre_tmp era '{convo.nombre_tmp}'")
                # Crear paciente minimal con fecha_nac por defecto
                try:
                    from datetime import date
                    # Validar que tenemos nombre y apellido
                    if not convo.nombre_tmp or not convo.apellido_tmp:
                        session.rollback()
                        return ConversationReply("Error: Datos incompletos. Intenta de nuevo.", "solicitar_nombre")
                    
                    paciente = CrearPacienteService.execute(
                        nombre=convo.nombre_tmp.strip(),
                        apellido=convo.apellido_tmp.strip(),
                        dni=convo.dni_propuesto,
                        fecha_nac=date(1990, 1, 1),  # Fecha por defecto para WhatsApp
                        telefono=convo.telefono_tmp,
                        direccion=None,
                        localidad_nombre=None,
                        localidad_id=None,
                        obra_social_id=None,
                        nro_afiliado=None,
                        titular=None,
                        parentesco=None,
                        lugar_trabajo=None,
                        barrio=None,
                    )
                    convo.paciente_id = paciente.id
                    convo.paso_actual = "solicitar_fecha"
                    session.commit()
                    return ConversationReply("Te registré. Indicá la fecha del turno (YYYY-MM-DD).", convo.paso_actual)
                except (PacienteDuplicadoError, DatosInvalidosPacienteError) as e:
                    session.rollback()
                    return ConversationReply(f"No pude registrarte: {str(e)}", step)

            if step == "solicitar_fecha":
                try:
                    fecha = datetime.strptime(message, "%Y-%m-%d").date()
                    convo.fecha_candidate = fecha
                    convo.paso_actual = "solicitar_hora"
                    session.commit()
                    session.refresh(convo)
                    return ConversationReply("Anotado. Indicá la hora (HH:MM).", convo.paso_actual)
                except ValueError:
                    session.commit()
                    return ConversationReply("Formato inválido. Usa YYYY-MM-DD.", step)

            if step == "solicitar_hora":
                try:
                    hora = datetime.strptime(message, "%H:%M").time()
                    convo.hora_candidate = hora
                    # Duración por defecto 30
                    duracion = convo.duracion_candidate or 30
                    turno = AgendarTurnoService.execute(
                        paciente_id=convo.paciente_id,
                        fecha=convo.fecha_candidate,
                        hora=hora,
                        duracion=duracion,
                        detalle=convo.detalle,
                        estado="Pendiente",  # WhatsApp siempre en Pendiente
                    )
                    convo.paso_actual = "completado"
                    convo.confirmed = False
                    session.commit()
                    session.refresh(convo)
                    return ConversationReply(
                        "Turno solicitado en estado Pendiente. La doctora confirmará el horario.",
                        convo.paso_actual,
                        done=True,
                    )
                except (TurnoError, PacienteNoEncontradoError) as e:
                    session.rollback()
                    return ConversationReply(f"No pude agendar: {str(e)}", step)
                except ValueError:
                    session.commit()
                    return ConversationReply("Formato inválido. Usa HH:MM.", step)

            # Default fallback
            session.commit()
            return ConversationReply("No entendí. Podés enviar tu DNI para comenzar.", step)
        except Exception:
            session.rollback()
            raise

    @staticmethod
    def reset(channel_user_id: str):
        session = ConversationService._get_session()
        convo = session.query(Conversation).filter_by(channel_user_id=channel_user_id).first()
        if convo:
            session.delete(convo)
            session.commit()

__all__ = ["ConversationService", "ConversationReply"]
