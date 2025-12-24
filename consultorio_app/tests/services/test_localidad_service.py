from app.services.localidad.crear_localidad_service import CrearLocalidadService
from app.models import Localidad


def test_crear_localidad(db_session):
    loc = CrearLocalidadService.crear("Salta")
    assert loc.id is not None
    assert Localidad.query.count() == 1
