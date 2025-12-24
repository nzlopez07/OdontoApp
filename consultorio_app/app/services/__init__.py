"""
Módulo de servicios refactorizado siguiendo arquitectura de casos de uso.

Estructura por dominio funcional:
- paciente/: Crear, editar, buscar pacientes
- turno/: Agendar, cambiar estado de turnos
- localidad/: Buscar, crear localidades
- obra_social/: Buscar obras sociales
- odontograma/: Obtener, crear versiones de odontogramas
- prestacion/: Listar prestaciones
- practica/: Listar prácticas
- common/: Excepciones y validadores reutilizables
- conversacion/: Placeholder para futura integración WhatsApp

Principios arquitectónicos:
- Cada service implementa UN caso de uso
- Sin imports de Flask
- Lógica de negocio encapsulada en services
- Routes son adaptadores HTTP delgados
- Excepciones propias para errores de negocio
"""


# Nuevos services por dominio
from .common import (
    OdontoAppError,
    PacienteError,
    PacienteNoEncontradoError,
    PacienteDuplicadoError,
    DatosInvalidosPacienteError,
    LocalidadError,
    LocalidadNoEncontradaError,
    TurnoError,
    TurnoNoEncontradoError,
    TurnoSolapamientoError,
    TurnoFechaInvalidaError,
    TurnoHoraInvalidaError,
    TurnoDuracionInvalidaError,
    TransicionEstadoInvalidaError,
    EstadoFinalError,
    TurnoYaAtendidoError,
    TurnoPendienteEliminableError,
    OdontogramaError,
    OdontogramaNoEncontradoError,
    ConversacionError,
    MensajeInvalidoError,
    BaseDatosError,
    TransactionError,
    ValidadorPaciente,
    ValidadorTurno,
    ValidadorLocalidad,
)

from .paciente import (
    CrearPacienteService,
    EditarPacienteService,
    BuscarPacientesService,
)

from .turno import (
    AgendarTurnoService,
    CambiarEstadoTurnoService,
    ObtenerAgendaService,
    ListarTurnosService,
    ObtenerHorariosService,
    EliminarTurnoService,
)

from .localidad import (
    BuscarLocalidadesService,
    CrearLocalidadService,
)

from .obra_social import (
    BuscarObrasSocialesService,
)

from .odontograma import (
    ObtenerOdontogramaService,
    CrearVersionOdontogramaService,
)

from .prestacion import (
    ListarPrestacionesService,
    CrearPrestacionService,
)

from .practica import (
    ListarPracticasService,
    CrearPracticaService,
    EditarPracticaService,
    EliminarPracticaService,
)

from .conversacion.conversation_service import (
    ConversationService,
    ConversationReply,
)

__all__ = [
    # Legacy utils
    'TurnoValidaciones',
    'FormateoUtils',
    'EstadoTurnoUtils',
    'BusquedaUtils',
    
    # Common (excepciones y validadores)
    'OdontoAppError',
    'PacienteError',
    'PacienteNoEncontradoError',
    'PacienteDuplicadoError',
    'DatosInvalidosPacienteError',
    'LocalidadError',
    'LocalidadNoEncontradaError',
    'TurnoError',
    'TurnoNoEncontradoError',
    'TurnoSolapamientoError',
    'TurnoFechaInvalidaError',
    'TurnoHoraInvalidaError',
    'TurnoDuracionInvalidaError',
    'TransicionEstadoInvalidaError',
    'EstadoFinalError',
    'TurnoYaAtendidoError',
    'TurnoPendienteEliminableError',
    'OdontogramaError',
    'OdontogramaNoEncontradoError',
    'ConversacionError',
    'MensajeInvalidoError',
    'BaseDatosError',
    'TransactionError',
    'ValidadorPaciente',
    'ValidadorTurno',
    'ValidadorLocalidad',
    
    # Paciente services
    'CrearPacienteService',
    'EditarPacienteService',
    'BuscarPacientesService',
    
    # Turno services
    'AgendarTurnoService',
    'CambiarEstadoTurnoService',
    'ObtenerAgendaService',
    'ListarTurnosService',
    'ObtenerHorariosService',
    'EliminarTurnoService',
    
    # Localidad services
    'BuscarLocalidadesService',
    'CrearLocalidadService',
    
    # ObraSocial services
    'BuscarObrasSocialesService',
    
    # Odontograma services
    'ObtenerOdontogramaService',
    'CrearVersionOdontogramaService',
    
    # Prestacion services
    'ListarPrestacionesService',
    'CrearPrestacionService',
    
    # Practica services
    'ListarPracticasService',
    'CrearPracticaService',
    'EditarPracticaService',
    'EliminarPracticaService',

    # Conversacion services
    'ConversationService',
    'ConversationReply',
]
