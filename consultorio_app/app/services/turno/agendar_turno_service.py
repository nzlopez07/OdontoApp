"""
AgendarTurnoService: Caso de uso para agendar un nuevo turno.

Responsabilidades:
- Validar datos del turno (fecha, hora, duración)
- Verificar disponibilidad (no solapamiento)
- Validar paciente existe
- Los turnos web siempre se crean en estado Confirmado
- Persistir turno
"""

from datetime import date, time, datetime, timedelta
from app.database.session import DatabaseSession
from app.models import Turno, Paciente, Estado
from app.services.common import (
    PacienteNoEncontradoError,
    TurnoError,
    TurnoFechaInvalidaError,
    TurnoHoraInvalidaError,
    TurnoDuracionInvalidaError,
    TurnoSolapamientoError,
    ValidadorTurno,
)


class AgendarTurnoService:
    """Caso de uso: agendar un nuevo turno."""
    
    @staticmethod
    def execute(
        paciente_id: int,
        fecha: date,
        hora: time,
        duracion: int = 30,
        detalle: str = None,
        estado: str = 'Confirmado',
    ) -> Turno:
        """
        Agenda un nuevo turno.
        
        Args:
            paciente_id: ID del paciente (requerido)
            fecha: Fecha del turno (requerido)
            hora: Hora del turno (requerido)
            duracion: Duración en minutos (default 30)
            detalle: Detalles/notas del turno (opcional)
            estado: Estado inicial del turno (default 'Confirmado'; use 'Pendiente' para WhatsApp)
        
        Returns:
            Turno agendado
        
        Raises:
            PacienteNoEncontradoError: Si paciente no existe
            TurnoFechaInvalidaError: Si fecha es inválida
            TurnoHoraInvalidaError: Si hora es fuera de rango
            TurnoDuracionInvalidaError: Si duración es inválida
            TurnoSolapamientoError: Si se solapa con otro turno
            TurnoError: Para otros errores
        """
        session = DatabaseSession.get_instance().session
        
        try:
            # Validar paciente existe
            paciente = Paciente.query.get(paciente_id)
            if not paciente:
                raise PacienteNoEncontradoError(paciente_id)
            
            # Validar fecha
            es_valida, mensaje = ValidadorTurno.validar_fecha(fecha)
            if not es_valida:
                raise TurnoFechaInvalidaError(mensaje)
            
            # Validar hora
            es_valida, mensaje = ValidadorTurno.validar_hora(hora)
            if not es_valida:
                raise TurnoHoraInvalidaError(mensaje)

            # Validar que fecha/hora no sean pasadas (mismo día con hora anterior)
            es_valida, mensaje = ValidadorTurno.validar_fecha_hora_futura(fecha, hora)
            if not es_valida:
                raise TurnoHoraInvalidaError(mensaje)
            
            # Validar duración
            es_valida, mensaje = ValidadorTurno.validar_duracion(duracion)
            if not es_valida:
                raise TurnoDuracionInvalidaError(duracion)
            
            # Validar que el turno no exceda el horario de fin
            hora_fin_turno = datetime.combine(date.today(), hora) + timedelta(minutes=duracion)
            if hora_fin_turno.time() > ValidadorTurno.HORARIO_FIN:
                raise TurnoError(
                    f"El turno terminaría a las {hora_fin_turno.strftime('%H:%M')}, "
                    f"después del horario de atención ({ValidadorTurno.HORARIO_FIN.strftime('%H:%M')}). "
                    f"Reduzca la duración o elija un horario más temprano."
                )
            
            # Verificar solapamiento
            AgendarTurnoService._verificar_solapamiento(fecha, hora, duracion)
            
            # Resolver estado por nombre (default Confirmado)
            estado_nombre = estado or 'Confirmado'
            estado_obj = Estado.query.filter_by(nombre=estado_nombre).first()
            if not estado_obj:
                raise TurnoError(f"Estado destino no encontrado en BD: '{estado_nombre}'")

            # Crear turno
            turno = Turno(
                paciente_id=paciente_id,
                fecha=fecha,
                hora=hora,
                duracion=duracion,
                detalle=detalle.strip() if detalle else None,
                estado=estado_obj.nombre,
                estado_id=estado_obj.id,
            )
            
            session.add(turno)
            session.commit()
            return turno
            
        except (PacienteNoEncontradoError, TurnoFechaInvalidaError, TurnoHoraInvalidaError,
                TurnoDuracionInvalidaError, TurnoSolapamientoError, TurnoError):
            session.rollback()
            raise
        except Exception as exc:
            session.rollback()
            raise TurnoError(f"Error al agendar turno: {str(exc)}")
    
    @staticmethod
    def _verificar_solapamiento(fecha: date, hora: time, duracion: int, turno_id_excluir: int = None) -> None:
        """
        Verifica que el turno no se solape con otros.
        
        Raises:
            TurnoSolapamientoError: Si hay solapamiento
        """
        inicio_min = hora.hour * 60 + hora.minute
        fin_min = inicio_min + duracion
        
        estados_excluir = {
            e.nombre: e.id for e in Estado.query.filter(Estado.nombre.in_(['Cancelado', 'NoAtendido'])).all()
        }
        ids_excluir = [eid for eid in [estados_excluir.get('Cancelado'), estados_excluir.get('NoAtendido')] if eid]

        query = Turno.query.filter(Turno.fecha == fecha)
        if ids_excluir:
            query = query.filter(~Turno.estado_id.in_(ids_excluir))
        if turno_id_excluir:
            query = query.filter(Turno.id != turno_id_excluir)
        
        turnos_dia = query.all()
        turnos_solapados = []
        
        for turno_existente in turnos_dia:
            if not turno_existente.hora:
                continue
            
            turno_inicio_min = turno_existente.hora.hour * 60 + turno_existente.hora.minute
            turno_duracion = getattr(turno_existente, 'duracion', 30)
            turno_fin_min = turno_inicio_min + turno_duracion
            
            # Verificar solapamiento
            if inicio_min < turno_fin_min and turno_inicio_min < fin_min:
                turnos_solapados.append(turno_existente)
        
        if turnos_solapados:
            detalles = []
            for t in turnos_solapados:
                t_fin = datetime.combine(date.today(), t.hora) + timedelta(minutes=getattr(t, 'duracion', 30))
                detalles.append(
                    f"{t.hora.strftime('%H:%M')}-{t_fin.strftime('%H:%M')} "
                    f"({t.paciente.nombre} {t.paciente.apellido})"
                )
            raise TurnoSolapamientoError(detalles)
