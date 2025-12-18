"""
Servicios para la gestión de turnos del consultorio odontológico.

Este módulo contiene la lógica de negocio para:
- Crear y gestionar turnos
- Validar disponibilidad de horarios
- Gestionar estados de turnos
- Notificaciones y recordatorios
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from app.database.session import DatabaseSession
from app.models import Turno, Paciente, Estado, CambioEstado


class TurnoService:
    """Servicio para la gestión de turnos."""
    
    # Configuración de horarios de trabajo
    HORARIO_INICIO = time(8, 0)  # 8:00 AM
    HORARIO_FIN = time(21, 0)    # 9:00 PM
    DURACION_TURNO = 30          # 30 minutos por turno
    DIAS_LABORABLES = [0, 1, 2, 3, 4]  # Lunes a Viernes (0=Lunes, 6=Domingo)
    
    @staticmethod
    def crear_turno(paciente_id: int, fecha: date, hora: time, 
                   observaciones: str = None) -> Dict[str, Any]:
        """
        Crea un nuevo turno para un paciente.
        
        Args:
            paciente_id: ID del paciente
            fecha: Fecha del turno
            hora: Hora del turno
            observaciones: Observaciones adicionales
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Validar que el paciente existe
            paciente = Paciente.query.get(paciente_id)
            if not paciente:
                return {
                    'success': False,
                    'error': 'Paciente no encontrado',
                    'turno': None
                }
            
            # Validar disponibilidad
            disponible = TurnoService.verificar_disponibilidad(fecha, hora)
            if not disponible['disponible']:
                return {
                    'success': False,
                    'error': disponible['motivo'],
                    'turno': None
                }
            
            # Obtener estado inicial (Pendiente)
            estado_pendiente = Estado.query.filter_by(nombre='Pendiente').first()
            if not estado_pendiente:
                return {
                    'success': False,
                    'error': 'Estado "Pendiente" no encontrado en el sistema',
                    'turno': None
                }
            
            # Crear el turno
            turno = Turno(
                paciente_id=paciente_id,
                fecha=fecha,
                hora=hora,
                estado_id=estado_pendiente.id,
                observaciones=observaciones,
                fecha_creacion=datetime.now()
            )
            
            session = DatabaseSession.get_instance().session
            session.add(turno)
            session.flush()  # Para obtener el ID del turno
            
            # Registrar cambio de estado inicial
            cambio_estado = CambioEstado(
                turno_id=turno.id,
                estado_anterior_id=None,
                estado_nuevo_id=estado_pendiente.id,
                fecha_cambio=datetime.now(),
                motivo='Turno creado'
            )
            
            session.add(cambio_estado)
            session.commit()
            
            return {
                'success': True,
                'error': None,
                'turno': turno
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Error al crear turno: {str(e)}',
                'turno': None
            }
    
    @staticmethod
    def verificar_disponibilidad(fecha: date, hora: time) -> Dict[str, Any]:
        """
        Verifica si un horario está disponible para agendar un turno.
        
        Args:
            fecha: Fecha a verificar
            hora: Hora a verificar
            
        Returns:
            Dict con información de disponibilidad
        """
        # Verificar que la fecha no sea en el pasado
        if fecha < date.today():
            return {
                'disponible': False,
                'motivo': 'No se pueden agendar turnos en fechas pasadas'
            }
        
        # Verificar que sea día laborable
        if fecha.weekday() not in TurnoService.DIAS_LABORABLES:
            return {
                'disponible': False,
                'motivo': 'Los turnos solo se pueden agendar de lunes a viernes'
            }
        
        # Verificar horario de trabajo
        if hora < TurnoService.HORARIO_INICIO or hora >= TurnoService.HORARIO_FIN:
            return {
                'disponible': False,
                'motivo': f'Los turnos solo se pueden agendar entre {TurnoService.HORARIO_INICIO.strftime("%H:%M")} y {TurnoService.HORARIO_FIN.strftime("%H:%M")}'
            }
        
        # Verificar que no haya otro turno en el mismo horario
        turno_existente = Turno.query.filter(
            and_(
                Turno.fecha == fecha,
                Turno.hora == hora
            )
        ).first()
        
        if turno_existente:
            return {
                'disponible': False,
                'motivo': 'Ya existe un turno agendado para ese horario'
            }
        
        return {
            'disponible': True,
            'motivo': None
        }
    
    @staticmethod
    def obtener_horarios_disponibles(fecha: date) -> List[time]:
        """
        Obtiene la lista de horarios disponibles para una fecha específica.
        
        Args:
            fecha: Fecha para consultar disponibilidad
            
        Returns:
            Lista de horarios disponibles
        """
        # Verificar que sea día laborable
        if fecha.weekday() not in TurnoService.DIAS_LABORABLES:
            return []
        
        # Generar todos los horarios posibles
        horarios_posibles = []
        hora_actual = TurnoService.HORARIO_INICIO
        
        while hora_actual < TurnoService.HORARIO_FIN:
            horarios_posibles.append(hora_actual)
            # Agregar duración del turno
            dt = datetime.combine(date.today(), hora_actual)
            dt += timedelta(minutes=TurnoService.DURACION_TURNO)
            hora_actual = dt.time()
        
        # Obtener turnos ya agendados para esa fecha
        turnos_agendados = Turno.query.filter_by(fecha=fecha).all()
        horarios_ocupados = [turno.hora for turno in turnos_agendados]
        
        # Filtrar horarios disponibles
        horarios_disponibles = [
            hora for hora in horarios_posibles 
            if hora not in horarios_ocupados
        ]
        
        return horarios_disponibles
    
    @staticmethod
    def cambiar_estado_turno(turno_id: int, nuevo_estado_nombre: str, 
                           motivo: str = None) -> Dict[str, Any]:
        """
        Cambia el estado de un turno.
        
        Args:
            turno_id: ID del turno
            nuevo_estado_nombre: Nombre del nuevo estado
            motivo: Motivo del cambio
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Obtener el turno
            turno = Turno.query.get(turno_id)
            if not turno:
                return {
                    'success': False,
                    'error': 'Turno no encontrado'
                }
            
            # Obtener el nuevo estado
            nuevo_estado = Estado.query.filter_by(nombre=nuevo_estado_nombre).first()
            if not nuevo_estado:
                return {
                    'success': False,
                    'error': f'Estado "{nuevo_estado_nombre}" no encontrado'
                }
            
            # Verificar que no sea el mismo estado
            if turno.estado_id == nuevo_estado.id:
                return {
                    'success': False,
                    'error': 'El turno ya tiene ese estado'
                }
            
            # Guardar estado anterior
            estado_anterior_id = turno.estado_id
            
            # Cambiar estado
            turno.estado_id = nuevo_estado.id
            
            # Registrar cambio de estado
            cambio_estado = CambioEstado(
                turno_id=turno_id,
                estado_anterior_id=estado_anterior_id,
                estado_nuevo_id=nuevo_estado.id,
                fecha_cambio=datetime.now(),
                motivo=motivo or f'Cambio a {nuevo_estado_nombre}'
            )
            
            session = DatabaseSession.get_instance().session
            session.add(cambio_estado)
            session.commit()
            
            return {
                'success': True,
                'error': None,
                'turno': turno
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Error al cambiar estado: {str(e)}'
            }
    
    @staticmethod
    def obtener_turnos_por_fecha(fecha: date) -> List[Turno]:
        """
        Obtiene todos los turnos para una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            
        Returns:
            Lista de turnos
        """
        return Turno.query.filter_by(fecha=fecha).order_by(Turno.hora).all()
    
    @staticmethod
    def obtener_turnos_por_paciente(paciente_id: int) -> List[Turno]:
        """
        Obtiene todos los turnos de un paciente.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Lista de turnos
        """
        return Turno.query.filter_by(paciente_id=paciente_id).order_by(
            Turno.fecha.desc(), Turno.hora.desc()
        ).all()
    
    @staticmethod
    def obtener_turnos_proximos(limite: int = 10) -> List[Turno]:
        """
        Obtiene los próximos turnos.
        
        Args:
            limite: Número máximo de turnos a retornar
            
        Returns:
            Lista de próximos turnos
        """
        return Turno.query.filter(
            Turno.fecha >= date.today()
        ).order_by(Turno.fecha, Turno.hora).limit(limite).all()

    # === Métodos adaptados a la app actual (estado como string) ===
    @staticmethod
    def actualizar_no_atendidos(session):
        """Marca turnos vencidos como NoAtendido."""
        ahora = datetime.now()
        hoy = date.today()

        vencidos = (
            session.query(Turno)
            .filter(Turno.estado.is_(None) | ~Turno.estado.in_(['Atendido', 'NoAtendido', 'Cancelado']))
            .all()
        )

        cambios = 0
        for turno in vencidos:
            es_vencido = False
            if turno.fecha < hoy:
                es_vencido = True
            elif turno.fecha == hoy and turno.hora:
                turno_dt = datetime.combine(turno.fecha, turno.hora)
                if turno_dt < ahora:
                    es_vencido = True
            if es_vencido:
                turno.estado = 'NoAtendido'
                cambios += 1
        if cambios:
            session.commit()

    @staticmethod
    def listar_turnos(fecha_filtro: str | None, termino: str | None):
        session = DatabaseSession.get_instance().session
        TurnoService.actualizar_no_atendidos(session)

        query = session.query(Turno).options(joinedload(Turno.paciente)).join(Paciente)

        if fecha_filtro:
            fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            query = query.filter(Turno.fecha == fecha_obj)
        else:
            query = query.filter(Turno.fecha >= date.today())

        termino = (termino or '').strip()
        if termino:
            like_term = f"%{termino.lower()}%"
            query = query.filter(
                (Paciente.nombre.ilike(like_term)) |
                (Paciente.apellido.ilike(like_term)) |
                (Paciente.dni.ilike(like_term))
            )

        return query.order_by(Turno.fecha, Turno.hora).all()

    @staticmethod
    def crear_turno(data: dict):
        session = DatabaseSession.get_instance().session
        turno = Turno(
            paciente_id=data.get('paciente_id'),
            fecha=data.get('fecha'),
            hora=data.get('hora'),
            detalle=data.get('detalle'),
            estado=data.get('estado', 'Pendiente'),
        )
        session.add(turno)
        session.commit()
        return turno

    @staticmethod
    def cambiar_estado(turno_id: int, nuevo_estado: str):
        session = DatabaseSession.get_instance().session
        turno = session.get(Turno, turno_id)
        if not turno:
            return None, 'Turno no encontrado'

        if nuevo_estado not in ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']:
            return None, 'Estado inválido'

        if nuevo_estado == 'Cancelado' and (turno.estado == 'NoAtendido'):
            return None, 'No se puede cancelar un turno marcado como NoAtendido.'

        estado_anterior = turno.estado or 'Pendiente'
        if turno.fecha < date.today() and nuevo_estado not in ['Atendido', 'NoAtendido']:
            turno.estado = 'NoAtendido'
        else:
            turno.estado = nuevo_estado

        cambio = CambioEstado(
            turno_id=turno.id,
            estado_anterior=estado_anterior,
            estado_nuevo=turno.estado,
            fecha_cambio=datetime.now(),
            motivo='Cambio de estado desde interfaz de usuario'
        )

        session.add(cambio)
        session.commit()
        return turno, None

    @staticmethod
    def eliminar_turno(turno_id: int):
        session = DatabaseSession.get_instance().session
        turno = session.get(Turno, turno_id)
        if not turno:
            return None, 'Turno no encontrado'
        estado_actual = turno.estado or 'Pendiente'
        if estado_actual != 'Pendiente':
            return None, f'Solo se pueden eliminar turnos Pendientes. Este turno está: {estado_actual}'
        session.delete(turno)
        session.commit()
        return turno, None
    
    @staticmethod
    def obtener_estadisticas_turnos() -> Dict[str, int]:
        """
        Obtiene estadísticas de turnos.
        
        Returns:
            Dict con estadísticas
        """
        total_turnos = Turno.query.count()
        turnos_hoy = Turno.query.filter_by(fecha=date.today()).count()
        
        # Turnos por estado
        estados = Estado.query.all()
        turnos_por_estado = {}
        
        for estado in estados:
            count = Turno.query.filter_by(estado_id=estado.id).count()
            turnos_por_estado[estado.nombre] = count
        
        return {
            'total_turnos': total_turnos,
            'turnos_hoy': turnos_hoy,
            **turnos_por_estado
        }
    
    @staticmethod
    def cancelar_turno(turno_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Cancela un turno.
        
        Args:
            turno_id: ID del turno a cancelar
            motivo: Motivo de la cancelación
            
        Returns:
            Dict con el resultado de la operación
        """
        return TurnoService.cambiar_estado_turno(
            turno_id, 'Cancelado', motivo or 'Turno cancelado'
        )
    
    @staticmethod
    def confirmar_turno(turno_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Confirma un turno.
        
        Args:
            turno_id: ID del turno a confirmar
            motivo: Motivo de la confirmación
            
        Returns:
            Dict con el resultado de la operación
        """
        return TurnoService.cambiar_estado_turno(
            turno_id, 'Confirmado', motivo or 'Turno confirmado'
        )
    
    @staticmethod
    def completar_turno(turno_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Marca un turno como completado.
        
        Args:
            turno_id: ID del turno a completar
            motivo: Motivo de la finalización
            
        Returns:
            Dict con el resultado de la operación
        """
        return TurnoService.cambiar_estado_turno(
            turno_id, 'Completado', motivo or 'Turno completado'
        )
