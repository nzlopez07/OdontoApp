"""
Configuración de logging para la aplicación.

Proporciona logging estructurado con niveles apropriados para
desarrollo y producción.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys


def configure_logging(app):
    """
    Configura el sistema de logging para la aplicación Flask.
    
    Soporta:
    - Logs en consola (stdout)
    - Logs en archivo con rotación (si LOG_DIR está configurado)
    - Niveles configurables (default: INFO)
    - Formatos estructurados
    
    Args:
        app: Instancia de Flask app
    """
    import os
    
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_dir = os.environ.get('LOG_DIR', '')
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Formato de logs
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo (si está configurado)
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'odonto.log'),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.setFormatter(log_format)
            root_logger.addHandler(file_handler)
            
            # Log de WhatsApp en archivo separado
            whatsapp_logger = logging.getLogger('whatsapp')
            whatsapp_handler = RotatingFileHandler(
                os.path.join(log_dir, 'whatsapp.log'),
                maxBytes=10 * 1024 * 1024,
                backupCount=3
            )
            whatsapp_handler.setLevel(getattr(logging, log_level))
            whatsapp_handler.setFormatter(log_format)
            whatsapp_logger.addHandler(whatsapp_handler)
            
        except Exception as e:
            root_logger.warning(f"Could not configure file logging: {str(e)}")
    
    # Configurar Flask app logger
    app.logger.setLevel(getattr(logging, log_level))
    
    # Loggers específicos por módulo
    logging.getLogger('app.services').setLevel(getattr(logging, log_level))
    logging.getLogger('app.adapters').setLevel(getattr(logging, log_level))
    logging.getLogger('app.routes').setLevel(getattr(logging, log_level))
    logging.getLogger('app.security').setLevel(getattr(logging, log_level))
    
    root_logger.info(f"Logging configured - Level: {log_level}")


__all__ = ["configure_logging"]
