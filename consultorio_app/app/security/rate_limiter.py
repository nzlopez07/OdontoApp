"""
Rate limiting simple por usuario/canal para prevenir abuso.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
import threading

# Lock para thread-safety
_rate_limit_lock = threading.RLock()

# Store de rate limits: {channel_user_id: [(timestamp, count), ...]}
_rate_limit_store: Dict[str, list] = {}


class RateLimiter:
    """Rate limiter simple en memoria."""
    
    # Configuración
    REQUESTS_PER_MINUTE = 5  # Máximo 5 mensajes por minuto por usuario
    CLEANUP_INTERVAL_MINUTES = 10
    
    @staticmethod
    def check_rate_limit(channel_user_id: str) -> Tuple[bool, str]:
        """
        Verifica si el usuario ha excedido el rate limit.
        
        Args:
            channel_user_id: ID del usuario (ej: número de WhatsApp)
        
        Returns:
            Tupla (allowed, message)
            - (True, "") si está dentro del límite
            - (False, "Rate limit exceeded...") si excedió
        """
        with _rate_limit_lock:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=1)
            
            if channel_user_id not in _rate_limit_store:
                _rate_limit_store[channel_user_id] = [(now, 1)]
                return True, ""
            
            # Limpiar registros viejos (> 1 minuto)
            records = _rate_limit_store[channel_user_id]
            records = [(ts, count) for ts, count in records if ts > window_start]
            
            # Contar mensajes en ventana
            message_count = sum(count for _, count in records)
            
            if message_count >= RateLimiter.REQUESTS_PER_MINUTE:
                return False, f"Rate limit exceeded. Max {RateLimiter.REQUESTS_PER_MINUTE} messages per minute."
            
            # Agregar nuevo registro
            records.append((now, 1))
            _rate_limit_store[channel_user_id] = records
            
            return True, ""
    
    @staticmethod
    def cleanup_old_entries():
        """Limpia entradas antiguas del store (ejecutar periódicamente)."""
        with _rate_limit_lock:
            now = datetime.utcnow()
            cleanup_window = now - timedelta(minutes=RateLimiter.CLEANUP_INTERVAL_MINUTES)
            
            for channel_user_id in list(_rate_limit_store.keys()):
                records = _rate_limit_store[channel_user_id]
                records = [(ts, count) for ts, count in records if ts > cleanup_window]
                
                if not records:
                    del _rate_limit_store[channel_user_id]
                else:
                    _rate_limit_store[channel_user_id] = records


__all__ = ["RateLimiter"]
