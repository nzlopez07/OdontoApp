# Importar todos los modelos para que SQLAlchemy los reconozca
from .paciente import Paciente
from .turno import Turno
from .estado import Estado
from .cambioEstado import CambioEstado
from .localidad import Localidad
from .obraSocial import ObraSocial
from .prestacion import Prestacion
from .codigo import Codigo
from .practica import Practica
from .prestacion_practica import PrestacionPractica
from .odontograma import Odontograma, OdontogramaCara
from .conversation import Conversation
from .usuario import Usuario
from .gasto import Gasto

# Lista de todos los modelos para facilitar la importación
__all__ = [
    'Paciente',
    'Turno', 
    'Estado',
    'CambioEstado',
    'Localidad',
    'ObraSocial',
    'Prestacion',
    'Codigo',
    'Practica',
    'PrestacionPractica',
    'Odontograma',
    'OdontogramaCara',
    'Conversation',
    'Usuario',
    'Gasto'
]
