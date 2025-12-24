"""
Tareas periódicas para mantenimiento de la aplicación.
"""

from datetime import datetime, date

from app.database import db
from app.models import Conversation, Turno


def cleanup_expired_conversations():
    """
    Elimina conversaciones que han expirado.
    
    Debe ejecutarse periodicamente (ej: cada 5 minutos) para mantener
    la tabla conversations limpia de intentos abandonados.
    """
    now = datetime.utcnow()
    
    # Buscar conversaciones expiradas
    expired_count = Conversation.query.filter(
        Conversation.expira_en < now
    ).delete()
    
    db.session.commit()
    
    if expired_count > 0:
        print(f"[cleanup] Eliminadas {expired_count} conversaciones expiradas")
    
    return expired_count


def actualizar_turnos_no_atendidos():
    """
    Marca como NoAtendido los turnos vencidos que no fueron atendidos.
    Reglas:
    - Turnos sin estado o con estado distinto de Atendido/NoAtendido/Cancelado.
    - Fecha pasada, o fecha de hoy con hora anterior a ahora.
    """
    ahora = datetime.now()
    hoy = date.today()
    
    turnos = Turno.query.filter(
        (Turno.estado.is_(None)) | (~Turno.estado.in_(['Atendido', 'NoAtendido', 'Cancelado']))
    ).all()
    
    cambios = 0
    for turno in turnos:
        vencido = False
        
        if turno.fecha and turno.fecha < hoy:
            vencido = True
        elif turno.fecha == hoy and turno.hora:
            turno_dt = datetime.combine(turno.fecha, turno.hora)
            if turno_dt < ahora:
                vencido = True
        
        if vencido:
            turno.estado = 'NoAtendido'
            cambios += 1
    
    if cambios:
        db.session.commit()
        print(f"[scheduler] Turnos marcados como NoAtendido: {cambios}")
    
    return cambios


def register_background_tasks(app):
    """
    Registra tareas periodicas usando APScheduler.
    
    Llama esta función desde create_app() después de crear la app Flask.
    
    Ejemplo:
        from app.scheduler import register_background_tasks
        
        app = create_app()
        register_background_tasks(app)
        app.run()
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        def _with_app_context(fn):
            """Envuelve la función para ejecutarla dentro del app_context y limpia la sesión."""
            def wrapper():
                with app.app_context():
                    try:
                        result = fn()
                        # Commit automático si no hubo excepción
                        if db.session.is_active:
                            db.session.commit()
                        return result
                    except Exception as e:
                        # Rollback automático en caso de error
                        db.session.rollback()
                        print(f"[scheduler] Error en job: {str(e)}")
                        raise
                    finally:
                        db.session.remove()
            return wrapper

        scheduler = BackgroundScheduler()
        
        # Cleanup de conversaciones cada 5 minutos
        scheduler.add_job(
            _with_app_context(cleanup_expired_conversations),
            'interval',
            minutes=5,
            id='cleanup_conversations',
            name='Cleanup conversaciones expiradas',
            replace_existing=True
        )

        # Actualizar turnos vencidos a NoAtendido cada 5 minutos
        scheduler.add_job(
            _with_app_context(actualizar_turnos_no_atendidos),
            'interval',
            minutes=5,
            id='actualizar_turnos_vencidos',
            name='Actualizar turnos vencidos',
            replace_existing=True
        )
        
        with app.app_context():
            scheduler.start()
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['apscheduler'] = scheduler
        print("[scheduler] Tareas periódicas registradas")
        
        return scheduler
    except ImportError:
        print(
            "[WARNING] APScheduler no instalado. "
            "Instala con: pip install apscheduler"
        )
        return None


__all__ = [
    "cleanup_expired_conversations",
    "actualizar_turnos_no_atendidos",
    "register_background_tasks",
]
