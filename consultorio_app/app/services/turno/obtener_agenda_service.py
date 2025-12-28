"""
Servicio para obtener la agenda visual de turnos con cálculos de posicionamiento.

Este servicio replica la lógica compleja de obtener_semana_agenda() del viejo
turno_service.py, calculando porcentajes de top y height para posicionamiento visual.
"""

from datetime import date, datetime, timedelta, time
from typing import Dict, List, Any
from app.database.session import DatabaseSession
from app.models import Turno, Paciente, Estado
from sqlalchemy.orm import joinedload


class ObtenerAgendaService:
    """Servicio para obtener agenda con visual positioning."""
    
    # Constantes de horario
    HORARIO_INICIO_HORA = 8
    HORARIO_INICIO_MIN = 0
    HORARIO_FIN_HORA = 21
    HORARIO_FIN_MIN = 0
    
    @staticmethod
    def obtener_semana_agenda(fecha_inicio: date) -> Dict[str, Any]:
        """
        Obtiene la agenda de una semana con cálculos de posicionamiento visual.
        
        Calcula top_pct y height_pct para cada turno para posicionarlos visualmente
        en un timeline que va de 8am a 9pm.
        
        Args:
            fecha_inicio: Fecha de inicio de la semana (generalmente un lunes)
            
        Returns:
            Dict con estructura:
            {
                'fecha_inicio': date,
                'fecha_fin': date,
                'turnos': [
                    {
                        'id': int,
                        'paciente': {'id': int, 'nombre': str, 'apellido': str, ...},
                        'fecha': date,
                        'hora': time,
                        'duracion': int,
                        'detalle': str,
                        'estado': str,
                        'top_pct': float,       # % desde 8am
                        'height_pct': float,    # % de altura
                        'hora_fin': time,
                    }
                ],
                'debug': {
                    'total_minutos_dia': int,
                    'horario_inicio_minutos': int,
                    'horario_fin_minutos': int,
                }
            }
        """
        session = DatabaseSession.get_instance().session
        
        # Calcular rango de la semana (lunes a domingo)
        dias_hasta_lunes = fecha_inicio.weekday()
        fecha_lunes = fecha_inicio - timedelta(days=dias_hasta_lunes)
        fecha_domingo = fecha_lunes + timedelta(days=6)

        # Armar contenedores por día (Lunes a Sábado como en UI)
        dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        semana = {}
        for i in range(6):
            fecha_dia = fecha_lunes + timedelta(days=i)
            semana[dias_nombres[i]] = {
                'fecha': fecha_dia,
                'bloques': [],
            }
        
        # Obtener id de Cancelado
        estado_cancelado = Estado.query.filter_by(nombre='Cancelado').first()
        estado_cancelado_id = estado_cancelado.id if estado_cancelado else None

        # Query turnos de la semana, ordenados por fecha y hora
        # Excluir solo cancelados; NoAtendido se muestra en agenda (reserva que no se atendió)
        filtros = [
            Turno.fecha >= fecha_lunes,
            Turno.fecha <= fecha_domingo,
        ]
        if estado_cancelado_id:
            filtros.append(Turno.estado_id != estado_cancelado_id)

        turnos = session.query(Turno).options(
            joinedload(Turno.paciente),
            joinedload(Turno.estado_obj),
        ).filter(*filtros).order_by(Turno.fecha, Turno.hora).all()
        
        # Calcular constantes de positioning
        horario_inicio_min = ObtenerAgendaService.HORARIO_INICIO_HORA * 60 + ObtenerAgendaService.HORARIO_INICIO_MIN  # 480
        horario_fin_min = ObtenerAgendaService.HORARIO_FIN_HORA * 60 + ObtenerAgendaService.HORARIO_FIN_MIN       # 1260
        total_minutos_dia = horario_fin_min - horario_inicio_min  # 780

        # Procesar cada turno y asignarlo al día correspondiente con posiciones visuales
        turnos_con_visual = []
        for turno in turnos:
            turno_hora_min = turno.hora.hour * 60 + turno.hora.minute
            offset_min = turno_hora_min - horario_inicio_min

            # Clipping: si turno comienza antes de 8am, mostrar desde 0%
            offset_min = max(0, offset_min)

            # Calcular porcentaje desde arriba
            top_pct = (offset_min / total_minutos_dia) * 100

            # Calcular altura del turno en porcentaje
            duracion_efectiva = turno.duracion

            # Edge case: si turno termina después de 9pm, truncar altura
            turno_fin_min = offset_min + turno.duracion
            if turno_fin_min > total_minutos_dia:
                duracion_efectiva = total_minutos_dia - offset_min

            height_pct = (duracion_efectiva / total_minutos_dia) * 100

            # Calcular hora de fin (solo informativo)
            hora_fin = (datetime.combine(date.today(), turno.hora) + timedelta(minutes=turno.duracion)).time()

            # Guardar estructura de turno visual (para APIs)
            turnos_con_visual.append({
                'id': turno.id,
                'paciente': {
                    'id': turno.paciente.id,
                    'nombre': turno.paciente.nombre,
                    'apellido': turno.paciente.apellido,
                    'dni': turno.paciente.dni,
                },
                'fecha': turno.fecha,
                'hora': turno.hora,
                'hora_fin': hora_fin,
                'duracion': turno.duracion,
                'detalle': turno.detalle,
                'estado': turno.estado_nombre,
                'top_pct': round(top_pct, 2),
                'height_pct': round(height_pct, 2),
                'truncado': turno_fin_min > total_minutos_dia,
            })

            # Asignar a semana para la vista (usa modelo Turno para compatibilidad con plantilla)
            dia_semana = turno.fecha.weekday()  # 0=Lunes
            if dia_semana < 6:
                dia_nombre = dias_nombres[dia_semana]
                semana[dia_nombre]['bloques'].append({
                    'turno': turno,
                    'top_pct': round(top_pct, 2),
                    'height_pct': round(height_pct, 2),
                })

        # Generar marcadores y labels horarios cada 1h (8 a 21)
        horas_marcadores = []
        horas_labels = []
        actual = datetime.combine(date.today(), time(ObtenerAgendaService.HORARIO_INICIO_HORA, ObtenerAgendaService.HORARIO_INICIO_MIN))
        fin = datetime.combine(date.today(), time(ObtenerAgendaService.HORARIO_FIN_HORA, ObtenerAgendaService.HORARIO_FIN_MIN))
        while actual <= fin:
            minutos_desde_inicio = (actual - datetime.combine(date.today(), time(ObtenerAgendaService.HORARIO_INICIO_HORA, ObtenerAgendaService.HORARIO_INICIO_MIN))).seconds // 60
            horas_marcadores.append((minutos_desde_inicio / total_minutos_dia) * 100.0)
            horas_labels.append(actual.strftime('%H:00'))
            actual += timedelta(hours=1)

        return {
            'semana': semana,
            'fecha_inicio': fecha_lunes,
            'fecha_fin': fecha_lunes + timedelta(days=5),  # Lunes a Sábado para la UI
            'semana_siguiente': fecha_lunes + timedelta(days=7),
            'semana_anterior': fecha_lunes - timedelta(days=7),
            'horas_marcadores': horas_marcadores,
            'horas_labels': horas_labels,
            'total_minutos_dia': total_minutos_dia,
            'turnos': turnos_con_visual,
            'debug': {
                'total_minutos_dia': total_minutos_dia,
                'horario_inicio_minutos': horario_inicio_min,
                'horario_fin_minutos': horario_fin_min,
            }
        }
    
    @staticmethod
    def obtener_dia_agenda(fecha: date) -> Dict[str, Any]:
        """
        Obtiene la agenda de un día específico con visual positioning.
        
        Args:
            fecha: Fecha del día a obtener
            
        Returns:
            Dict con estructura similar a obtener_semana_agenda pero para un día
        """
        session = DatabaseSession.get_instance().session
        
        # Query turnos del día
        # Excluir solo cancelados; NoAtendido se muestra en agenda (reserva que no se atendió)
        estado_cancelado = Estado.query.filter_by(nombre='Cancelado').first()
        estado_cancelado_id = estado_cancelado.id if estado_cancelado else None

        filtros = [Turno.fecha == fecha]
        if estado_cancelado_id:
            filtros.append(Turno.estado_id != estado_cancelado_id)

        turnos = session.query(Turno).options(
            joinedload(Turno.paciente),
            joinedload(Turno.estado_obj),
        ).filter(*filtros).order_by(Turno.hora).all()
        
        # Calcular constantes
        horario_inicio_min = ObtenerAgendaService.HORARIO_INICIO_HORA * 60 + ObtenerAgendaService.HORARIO_INICIO_MIN
        horario_fin_min = ObtenerAgendaService.HORARIO_FIN_HORA * 60 + ObtenerAgendaService.HORARIO_FIN_MIN
        total_minutos_dia = horario_fin_min - horario_inicio_min
        
        # Procesar turnos igual que en obtener_semana_agenda
        turnos_con_visual = []
        for turno in turnos:
            turno_hora_min = turno.hora.hour * 60 + turno.hora.minute
            offset_min = turno_hora_min - horario_inicio_min
            offset_min = max(0, offset_min)
            
            top_pct = (offset_min / total_minutos_dia) * 100
            
            duracion_efectiva = turno.duracion
            turno_fin_min = offset_min + turno.duracion
            if turno_fin_min > total_minutos_dia:
                duracion_efectiva = total_minutos_dia - offset_min
            
            height_pct = (duracion_efectiva / total_minutos_dia) * 100
            
            hora_fin = (datetime.combine(date.today(), turno.hora) + timedelta(minutes=turno.duracion)).time()
            
            turno_dict = {
                'id': turno.id,
                'paciente': {
                    'id': turno.paciente.id,
                    'nombre': turno.paciente.nombre,
                    'apellido': turno.paciente.apellido,
                    'dni': turno.paciente.dni,
                },
                'fecha': turno.fecha,
                'hora': turno.hora,
                'hora_fin': hora_fin,
                'duracion': turno.duracion,
                'detalle': turno.detalle,
                'estado': turno.estado_nombre,
                'top_pct': round(top_pct, 2),
                'height_pct': round(height_pct, 2),
                'truncado': turno_fin_min > total_minutos_dia,
            }
            turnos_con_visual.append(turno_dict)
        
        return {
            'fecha': fecha,
            'turnos': turnos_con_visual,
            'debug': {
                'total_minutos_dia': total_minutos_dia,
                'horario_inicio_minutos': horario_inicio_min,
                'horario_fin_minutos': horario_fin_min,
            }
        }
