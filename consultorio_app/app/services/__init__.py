"""
Módulo de servicios del sistema de gestión de consultorio odontológico.

Este módulo contiene la lógica de negocio del sistema, separada de las rutas
y la presentación. Los servicios encapsulan las operaciones complejas y
proporcionan una interfaz limpia para las diferentes funcionalidades.

Servicios disponibles:
- TurnoService: Gestión de turnos y citas
- TurnoValidaciones: Validaciones específicas para turnos
- FormateoUtils: Utilidades de formateo
- EstadoTurnoUtils: Utilidades para manejo de estados
- BusquedaUtils: Utilidades para búsqueda flexible de texto
"""

from .turno_service import TurnoService
from .turno_utils import TurnoValidaciones, FormateoUtils, EstadoTurnoUtils
from .busqueda_utils import BusquedaUtils

__all__ = [
    'TurnoService',
    'TurnoValidaciones',
    'FormateoUtils',
    'EstadoTurnoUtils',
    'BusquedaUtils',
]
