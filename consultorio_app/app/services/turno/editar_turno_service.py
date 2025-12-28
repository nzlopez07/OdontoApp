"""
EditarTurnoService: Caso de uso para editar/reagendar un turno existente.

Responsabilidades:
- Validar que el turno no esté en estado final
- Validar nueva fecha y hora
- Verificar disponibilidad sin solapamiento
- Persistir cambios
"""

from datetime import date, time, datetime, timedelta
from app.database.session import DatabaseSession
from app.models import Turno
from app.services.common import (
    TurnoNoEncontradoError,
    TurnoError,
    TurnoFechaInvalidaError,
    TurnoHoraInvalidaError,
    TurnoDuracionInvalidaError,
    TurnoSolapamientoError,
    ValidadorTurno,
    EstadoFinalError,
)


class EditarTurnoService:
    """Caso de uso: editar/reagendar un turno existente."""
    
    @staticmethod
    def execute(
        turno_id: int,
        fecha: date = None,
        hora: time = None,
        duracion: int = None,
        detalle: str = None,
    ) -> Turno:
        """
        Edita un turno existente. Solo se pueden editar turnos que no están en estado final.
        
        Args:
            turno_id: ID del turno a editar
            fecha: Nueva fecha (opcional)
            hora: Nueva hora (opcional)
            duracion: Nueva duración en minutos (opcional)
            detalle: Nuevos detalles (opcional)
        
        Returns:
            Turno editado
        
        Raises:
            TurnoNoEncontradoError: Si turno no existe
            EstadoFinalError: Si turno está en estado final
            TurnoFechaInvalidaError: Si fecha es inválida
            TurnoHoraInvalidaError: Si hora es fuera de rango
            TurnoDuracionInvalidaError: Si duración es inválida
            TurnoSolapamientoError: Si nueva fecha/hora se solapa con otro turno
            TurnoError: Para otros errores
        """
        session = DatabaseSession.get_instance().session
        
        try:
            # Obtener turno
            turno = session.get(Turno, turno_id)
            if not turno:
                raise TurnoNoEncontradoError(turno_id)
            
            # Verificar que no está en estado final
            estado_actual = turno.estado_nombre
            estados_finales = ['Atendido', 'NoAtendido', 'Cancelado']
            if estado_actual in estados_finales:
                raise EstadoFinalError(
                    f"No se puede reagendar un turno en estado '{estado_actual}'. "
                    f"Solo se pueden reagendar turnos en estados: Pendiente, Confirmado."
                )
            
            # Validar y actualizar fecha si se proporciona
            if fecha is not None:
                es_valida, mensaje = ValidadorTurno.validar_fecha(fecha)
                if not es_valida:
                    raise TurnoFechaInvalidaError(mensaje)
                turno.fecha = fecha
            
            # Validar y actualizar hora si se proporciona
            if hora is not None:
                es_valida, mensaje = ValidadorTurno.validar_hora(hora)
                if not es_valida:
                    raise TurnoHoraInvalidaError(mensaje)
                turno.hora = hora
            
            # Validar y actualizar duración si se proporciona
            if duracion is not None:
                es_valida, mensaje = ValidadorTurno.validar_duracion(duracion)
                if not es_valida:
                    raise TurnoDuracionInvalidaError(duracion)
                turno.duracion = duracion
            
            # Si se cambió fecha o hora, validar que no exceda horario de fin
            if fecha is not None or hora is not None:
                fecha_check = turno.fecha
                hora_check = turno.hora
                duracion_check = turno.duracion

                # No permitir reagendar a una hora pasada del día actual
                es_valida, mensaje = ValidadorTurno.validar_fecha_hora_futura(fecha_check, hora_check)
                if not es_valida:
                    raise TurnoHoraInvalidaError(mensaje)
                
                hora_fin_turno = datetime.combine(date.today(), hora_check) + timedelta(minutes=duracion_check)
                if hora_fin_turno.time() > ValidadorTurno.HORARIO_FIN:
                    raise TurnoError(
                        f"El turno terminaría a las {hora_fin_turno.strftime('%H:%M')}, "
                        f"después del horario de atención ({ValidadorTurno.HORARIO_FIN.strftime('%H:%M')}). "
                        f"Reduzca la duración o elija un horario más temprano."
                    )
                
                # Verificar solapamiento con la nueva fecha/hora
                EditarTurnoService._verificar_solapamiento(
                    fecha_check, hora_check, duracion_check, turno_id_excluir=turno_id
                )
            
            # Actualizar detalle si se proporciona
            if detalle is not None:
                turno.detalle = detalle.strip() if detalle else None
            
            session.commit()
            return turno
            
        except (TurnoNoEncontradoError, EstadoFinalError, TurnoFechaInvalidaError, 
                TurnoHoraInvalidaError, TurnoDuracionInvalidaError, TurnoSolapamientoError, 
                TurnoError):
            session.rollback()
            raise
        except Exception as exc:
            session.rollback()
            raise TurnoError(f"Error al editar turno: {str(exc)}")
    
    @staticmethod
    def _verificar_solapamiento(fecha: date, hora: time, duracion: int, turno_id_excluir: int = None) -> None:
        """
        Verifica que el turno no se solape con otros (excluyendo Cancelado/NoAtendido).
        
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
