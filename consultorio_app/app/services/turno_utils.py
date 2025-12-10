"""
Utilidades y validaciones comunes para los servicios de turnos.

Este módulo contiene funciones auxiliares y validaciones que son utilizadas
por múltiples servicios del sistema.
"""

from datetime import datetime, date, time
from typing import Dict, Any, List
import re


class TurnoValidaciones:
    """Clase con validaciones específicas para turnos."""
    
    @staticmethod
    def validar_fecha_turno(fecha: date) -> Dict[str, Any]:
        """
        Valida que una fecha sea válida para agendar turnos.
        
        Args:
            fecha: Fecha a validar
            
        Returns:
            Dict con resultado de validación
        """
        if not isinstance(fecha, date):
            return {
                'valido': False,
                'error': 'La fecha debe ser un objeto date válido'
            }
        
        # No permitir fechas en el pasado
        if fecha < date.today():
            return {
                'valido': False,
                'error': 'No se pueden agendar turnos en fechas pasadas'
            }
        
        # No permitir fechas muy futuras (más de 6 meses)
        fecha_limite = date.today().replace(month=date.today().month + 6)
        if fecha > fecha_limite:
            return {
                'valido': False,
                'error': 'No se pueden agendar turnos con más de 6 meses de anticipación'
            }
        
        return {
            'valido': True,
            'error': None
        }
    
    @staticmethod
    def validar_hora_turno(hora: time) -> Dict[str, Any]:
        """
        Valida que una hora sea válida para turnos.
        
        Args:
            hora: Hora a validar
            
        Returns:
            Dict con resultado de validación
        """
        if not isinstance(hora, time):
            return {
                'valido': False,
                'error': 'La hora debe ser un objeto time válido'
            }
        
        # Validar formato de minutos (solo :00 o :30)
        if hora.minute not in [0, 30]:
            return {
                'valido': False,
                'error': 'Los turnos solo pueden agendarse en horarios de 30 minutos (:00 o :30)'
            }
        
        return {
            'valido': True,
            'error': None
        }
    
    @staticmethod
    def validar_observaciones(observaciones: str) -> Dict[str, Any]:
        """
        Valida las observaciones de un turno.
        
        Args:
            observaciones: Texto de observaciones
            
        Returns:
            Dict con resultado de validación
        """
        if observaciones is None:
            return {
                'valido': True,
                'error': None
            }
        
        if not isinstance(observaciones, str):
            return {
                'valido': False,
                'error': 'Las observaciones deben ser texto'
            }
        
        # Máximo 500 caracteres
        if len(observaciones) > 500:
            return {
                'valido': False,
                'error': 'Las observaciones no pueden exceder 500 caracteres'
            }
        
        return {
            'valido': True,
            'error': None
        }


class FormateoUtils:
    """Utilidades para formateo de datos."""
    
    @staticmethod
    def formatear_fecha(fecha: date) -> str:
        """
        Formatea una fecha para mostrar al usuario.
        
        Args:
            fecha: Fecha a formatear
            
        Returns:
            Fecha formateada como string
        """
        if not fecha:
            return ''
        
        meses = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        
        dias_semana = [
            'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'
        ]
        
        dia_semana = dias_semana[fecha.weekday()]
        mes = meses[fecha.month - 1]
        
        return f"{dia_semana} {fecha.day} de {mes} de {fecha.year}"
    
    @staticmethod
    def formatear_hora(hora: time) -> str:
        """
        Formatea una hora para mostrar al usuario.
        
        Args:
            hora: Hora a formatear
            
        Returns:
            Hora formateada como string
        """
        if not hora:
            return ''
        
        return hora.strftime('%H:%M')
    
    @staticmethod
    def formatear_duracion(minutos: int) -> str:
        """
        Formatea una duración en minutos a formato legible.
        
        Args:
            minutos: Duración en minutos
            
        Returns:
            Duración formateada
        """
        if minutos < 60:
            return f"{minutos} minutos"
        
        horas = minutos // 60
        minutos_restantes = minutos % 60
        
        if minutos_restantes == 0:
            return f"{horas} hora{'s' if horas > 1 else ''}"
        
        return f"{horas} hora{'s' if horas > 1 else ''} y {minutos_restantes} minutos"


class EstadoTurnoUtils:
    """Utilidades para manejo de estados de turnos."""
    
    # Estados válidos y sus transiciones permitidas
    TRANSICIONES_PERMITIDAS = {
        'Pendiente': ['Confirmado', 'Cancelado'],
        'Confirmado': ['Completado', 'Cancelado', 'Reagendado'],
        'Completado': [],  # Estado final
        'Cancelado': ['Pendiente'],  # Se puede reactivar
        'Reagendado': []  # Estado final
    }
    
    ESTADOS_ACTIVOS = ['Pendiente', 'Confirmado']
    ESTADOS_FINALES = ['Completado', 'Cancelado', 'Reagendado']
    
    @staticmethod
    def validar_transicion_estado(estado_actual: str, estado_nuevo: str) -> Dict[str, Any]:
        """
        Valida si una transición de estado es válida.
        
        Args:
            estado_actual: Estado actual del turno
            estado_nuevo: Estado al que se quiere cambiar
            
        Returns:
            Dict con resultado de validación
        """
        if estado_actual not in EstadoTurnoUtils.TRANSICIONES_PERMITIDAS:
            return {
                'valido': False,
                'error': f'Estado actual "{estado_actual}" no reconocido'
            }
        
        estados_permitidos = EstadoTurnoUtils.TRANSICIONES_PERMITIDAS[estado_actual]
        
        if estado_nuevo not in estados_permitidos:
            return {
                'valido': False,
                'error': f'No se puede cambiar de "{estado_actual}" a "{estado_nuevo}"'
            }
        
        return {
            'valido': True,
            'error': None
        }
    
    @staticmethod
    def es_estado_activo(estado: str) -> bool:
        """
        Determina si un estado es activo (el turno aún puede modificarse).
        
        Args:
            estado: Nombre del estado
            
        Returns:
            True si el estado es activo
        """
        return estado in EstadoTurnoUtils.ESTADOS_ACTIVOS
    
    @staticmethod
    def es_estado_final(estado: str) -> bool:
        """
        Determina si un estado es final (el turno no puede modificarse más).
        
        Args:
            estado: Nombre del estado
            
        Returns:
            True si el estado es final
        """
        return estado in EstadoTurnoUtils.ESTADOS_FINALES
    
    @staticmethod
    def obtener_estados_siguientes(estado_actual: str) -> List[str]:
        """
        Obtiene los estados a los que se puede transicionar.
        
        Args:
            estado_actual: Estado actual
            
        Returns:
            Lista de estados válidos para transición
        """
        return EstadoTurnoUtils.TRANSICIONES_PERMITIDAS.get(estado_actual, [])
