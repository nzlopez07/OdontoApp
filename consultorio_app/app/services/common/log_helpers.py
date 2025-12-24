"""
Helpers para logging seguro.

NUNCA loggear datos clínicos directamente.
Siempre usar estos helpers para eventos que involucren entidades con datos sensibles.
"""

import logging
from typing import Optional


def log_paciente_event(event: str, paciente_id: int, extra: Optional[dict] = None):
    """
    Loggea un evento relacionado a un paciente SIN exponer datos sensibles.
    
    Args:
        event: Descripción del evento (ej: 'creado', 'actualizado', 'eliminado')
        paciente_id: ID del paciente (nunca nombre/DNI)
        extra: Información técnica adicional (sin datos personales)
    """
    logger = logging.getLogger('app.services.paciente')
    msg = f"Paciente {event}: paciente_id={paciente_id}"
    
    if extra:
        # Filtrar cualquier campo sensible que pudiera colarse
        safe_extra = {k: v for k, v in extra.items() 
                     if k not in ['nombre', 'apellido', 'dni', 'email', 'telefono', 'direccion']}
        if safe_extra:
            msg += f" | {safe_extra}"
    
    logger.info(msg)


def log_turno_event(event: str, turno_id: int, paciente_id: Optional[int] = None, 
                    fecha: Optional[str] = None, estado: Optional[str] = None):
    """
    Loggea un evento de turno.
    
    Args:
        event: Descripción del evento
        turno_id: ID del turno
        paciente_id: ID del paciente (opcional)
        fecha: Fecha del turno en formato ISO (opcional)
        estado: Estado del turno (opcional)
    """
    logger = logging.getLogger('app.services.turno')
    msg = f"Turno {event}: turno_id={turno_id}"
    
    if paciente_id:
        msg += f", paciente_id={paciente_id}"
    if fecha:
        msg += f", fecha={fecha}"
    if estado:
        msg += f", estado={estado}"
    
    logger.info(msg)


def log_prestacion_event(event: str, prestacion_id: int, paciente_id: Optional[int] = None,
                        monto: Optional[float] = None, practicas_count: Optional[int] = None):
    """
    Loggea un evento de prestación.
    
    NOTA: El monto es técnicamente un dato sensible, pero útil para auditoría.
    Solo loggear si es estrictamente necesario.
    
    Args:
        event: Descripción del evento
        prestacion_id: ID de la prestación
        paciente_id: ID del paciente (opcional)
        monto: Monto total (opcional, solo para eventos importantes)
        practicas_count: Cantidad de prácticas (opcional)
    """
    logger = logging.getLogger('app.services.prestacion')
    msg = f"Prestación {event}: prestacion_id={prestacion_id}"
    
    if paciente_id:
        msg += f", paciente_id={paciente_id}"
    if practicas_count:
        msg += f", practicas={practicas_count}"
    if monto is not None:
        # Solo loggear monto en creación/eliminación, no en consultas
        if event in ['creada', 'eliminada']:
            msg += f", monto={monto:.2f}"
    
    logger.info(msg)


def log_security_event(event: str, username: Optional[str] = None, 
                       user_id: Optional[int] = None, success: bool = True,
                       ip_address: Optional[str] = None, extra: Optional[str] = None):
    """
    Loggea eventos de seguridad (login, permisos, etc).
    
    Args:
        event: Tipo de evento (login, logout, permission_denied, etc)
        username: Nombre de usuario (opcional)
        user_id: ID del usuario (opcional)
        success: Si la operación fue exitosa
        ip_address: IP del cliente (opcional)
        extra: Información adicional
    """
    logger = logging.getLogger('security')
    
    status = 'SUCCESS' if success else 'FAILED'
    msg = f"{event.upper()} | {status}"
    
    if username:
        msg += f" | user={username}"
    if user_id:
        msg += f" | user_id={user_id}"
    if ip_address:
        msg += f" | ip={ip_address}"
    if extra:
        msg += f" | {extra}"
    
    if success:
        logger.info(msg)
    else:
        logger.warning(msg)


def log_whatsapp_event(event: str, phone_number: Optional[str] = None,
                      message_id: Optional[str] = None, success: bool = True,
                      error: Optional[str] = None):
    """
    Loggea eventos de WhatsApp.
    
    Args:
        event: Tipo de evento (message_sent, message_received, etc)
        phone_number: Número de teléfono (últimos 4 dígitos solo)
        message_id: ID del mensaje
        success: Si la operación fue exitosa
        error: Mensaje de error si hubo fallo
    """
    logger = logging.getLogger('whatsapp')
    
    msg = f"{event}"
    
    if phone_number:
        # Solo loggear últimos 4 dígitos para privacidad
        masked = f"****{phone_number[-4:]}" if len(phone_number) > 4 else "****"
        msg += f" | phone={masked}"
    
    if message_id:
        msg += f" | msg_id={message_id}"
    
    if not success and error:
        msg += f" | error={error}"
    
    if success:
        logger.info(msg)
    else:
        logger.error(msg)


def log_database_event(event: str, table: Optional[str] = None, 
                      record_id: Optional[int] = None, extra: Optional[dict] = None):
    """
    Loggea operaciones de base de datos (backup, restore, migrations).
    
    Args:
        event: Tipo de evento (backup, restore, migration, etc)
        table: Tabla afectada (opcional)
        record_id: ID del registro (opcional)
        extra: Información técnica adicional
    """
    logger = logging.getLogger('app.database')
    
    msg = f"DB {event}"
    
    if table:
        msg += f" | table={table}"
    if record_id:
        msg += f" | id={record_id}"
    if extra:
        msg += f" | {extra}"
    
    logger.info(msg)


def log_error(error: Exception, context: Optional[str] = None, extra: Optional[dict] = None):
    """
    Loggea un error/excepción con contexto.
    
    Args:
        error: La excepción capturada
        context: Contexto donde ocurrió el error
        extra: Información adicional técnica
    """
    logger = logging.getLogger('app.errors')
    
    msg = f"{error.__class__.__name__}: {str(error)}"
    
    if context:
        msg = f"[{context}] {msg}"
    
    if extra:
        # Filtrar datos sensibles
        safe_extra = {k: v for k, v in extra.items() 
                     if k not in ['nombre', 'apellido', 'dni', 'email', 'password']}
        if safe_extra:
            msg += f" | {safe_extra}"
    
    logger.error(msg, exc_info=True)
