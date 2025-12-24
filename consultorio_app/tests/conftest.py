"""Fixtures base para pytest."""

import os
import pytest

from app import create_app
from app.database import db


@pytest.fixture(scope="session")
def app():
    """Crea una app Flask para tests con SQLite en memoria y sin scheduler."""
    os.environ.setdefault("TESTING", "1")
    os.environ.setdefault("DISABLE_SCHEDULER", "1")
    os.environ.setdefault("FLASK_LOGIN_DISABLED", "1")  # se puede habilitar por test si se requiere

    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    """Cliente de pruebas de Flask."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Sesión de DB aislada por test (rollback + cleanup)."""
    with app.app_context():
        try:
            yield db.session
            db.session.commit()
        finally:
            db.session.rollback()
            # Limpiar todas las tablas para el siguiente test
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
