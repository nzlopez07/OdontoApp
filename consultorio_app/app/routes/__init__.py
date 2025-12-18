from flask import Blueprint

# Blueprint único para mantener los mismos endpoint names (main.*)
main_bp = Blueprint('main', __name__)

# Registrar rutas separadas por dominio/servicio
from . import index  # noqa: E402,F401
from . import pacientes  # noqa: E402,F401
from . import turnos  # noqa: E402,F401
from . import prestaciones  # noqa: E402,F401
from . import api  # noqa: E402,F401

__all__ = ['main_bp']
