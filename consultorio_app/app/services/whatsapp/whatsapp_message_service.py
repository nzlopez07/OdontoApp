"""
Servicio para enviar mensajes vía WhatsApp Cloud API.

Responsabilidades:
- Enviar ConversationReply al usuario vía WhatsApp API
- Manejo de errores y reintentos
- Logging de intentos y fallos
"""

import os
import logging
import requests
from typing import Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppMessageService:
    """Servicio para enviar mensajes a través de WhatsApp Cloud API."""
    
    # Configuración de API (WhatsApp usa Graph Facebook, NO Instagram)
    WHATSAPP_API_VERSION = "v22.0"
    WHATSAPP_API_BASE_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}"
    
    # Reintentos
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2
    
    # Timeouts
    REQUEST_TIMEOUT = 10
    
    @staticmethod
    def _get_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Obtiene credenciales de variables de entorno.
        
        Returns:
            Tupla (access_token, phone_number_id, business_account_id) o (None, None, None)
        """
        access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        biz_id = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID')
        
        if not access_token or not phone_id:
            logger.warning(
                "WhatsApp credentials not configured. "
                "Set WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID"
            )
            return None, None, None
        
        return access_token, phone_id, biz_id
    
    @staticmethod
    def send_text_message(
        phone_number: str,
        message_text: str,
        retry_count: int = 0
    ) -> Tuple[bool, str]:
        """
        Envía un mensaje de texto a un usuario.
        
        Args:
            phone_number: Número de teléfono destino (formato E.164: 34612345678)
            message_text: Texto a enviar
            retry_count: Número de reintento actual (uso interno)
        
        Returns:
            Tupla (success, message_id_or_error)
            - (True, message_id) si fue exitoso
            - (False, error_description) si falló
        """
        access_token, phone_id, _ = WhatsAppMessageService._get_credentials()
        
        if not access_token:
            return False, "WhatsApp credentials not configured"
        
        # Validar número (E.164)
        if not WhatsAppMessageService._is_valid_e164(phone_number):
            logger.warning(f"Invalid phone number format: {phone_number}")
            return False, "Invalid phone number format (use E.164: 34612345678)"
        
        url = f"{WhatsAppMessageService.WHATSAPP_API_BASE_URL}/{phone_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        try:
            logger.info(f"Sending WhatsApp message to {phone_number}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=WhatsAppMessageService.REQUEST_TIMEOUT
            )
            
            # Loguear respuesta
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"Message sent successfully. ID: {message_id}")
                return True, message_id
            
            elif response.status_code == 429:
                # Rate limit: reintentar
                if retry_count < WhatsAppMessageService.MAX_RETRIES:
                    logger.warning(
                        f"Rate limited (429). Retrying... ({retry_count + 1}/{WhatsAppMessageService.MAX_RETRIES})"
                    )
                    import time
                    time.sleep(WhatsAppMessageService.RETRY_DELAY_SECONDS)
                    return WhatsAppMessageService.send_text_message(
                        phone_number,
                        message_text,
                        retry_count + 1
                    )
                else:
                    error = "Rate limited (429) - max retries exceeded"
                    logger.error(error)
                    return False, error
            
            elif response.status_code == 401:
                error = "Unauthorized - check WHATSAPP_ACCESS_TOKEN"
                logger.error(error)
                return False, error
            
            elif response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', {}).get('message', 'Bad request')
                logger.error(f"Bad request (400): {error_msg}")
                return False, f"Bad request: {error_msg}"
            
            else:
                error = f"WhatsApp API error ({response.status_code}): {response.text}"
                logger.error(error)
                return False, error
        
        except requests.exceptions.Timeout:
            if retry_count < WhatsAppMessageService.MAX_RETRIES:
                logger.warning(f"Timeout. Retrying... ({retry_count + 1}/{WhatsAppMessageService.MAX_RETRIES})")
                import time
                time.sleep(WhatsAppMessageService.RETRY_DELAY_SECONDS)
                return WhatsAppMessageService.send_text_message(
                    phone_number,
                    message_text,
                    retry_count + 1
                )
            else:
                error = "Request timeout - max retries exceeded"
                logger.error(error)
                return False, error
        
        except requests.exceptions.ConnectionError as e:
            if retry_count < WhatsAppMessageService.MAX_RETRIES:
                logger.warning(f"Connection error. Retrying... ({retry_count + 1}/{WhatsAppMessageService.MAX_RETRIES})")
                import time
                time.sleep(WhatsAppMessageService.RETRY_DELAY_SECONDS)
                return WhatsAppMessageService.send_text_message(
                    phone_number,
                    message_text,
                    retry_count + 1
                )
            else:
                error = f"Connection error - max retries exceeded: {str(e)}"
                logger.error(error)
                return False, error
        
        except Exception as e:
            error = f"Unexpected error sending message: {str(e)}"
            logger.exception(error)
            return False, error

    @staticmethod
    def send_template_message(
        phone_number: str,
        template_name: str,
        language_code: str = "en_US",
        retry_count: int = 0
    ) -> Tuple[bool, str]:
        """
        Envía un mensaje de plantilla (template) para iniciar conversación fuera de la ventana de 24h.
        Útil para pruebas de sandbox.

        Args:
            phone_number: Número destino en formato E.164 sin "+" (ej: 5491123456789)
            template_name: Nombre de la plantilla aprobada (ej: "jaspers_market_plain_text_v1")
            language_code: Código de idioma de la plantilla (ej: "en_US")
            retry_count: Reintentos en caso de 429/timeout

        Returns:
            Tupla (success, message_id_or_error)
        """
        access_token, phone_id, _ = WhatsAppMessageService._get_credentials()
        if not access_token:
            return False, "WhatsApp credentials not configured"

        if not WhatsAppMessageService._is_valid_e164(phone_number):
            logger.warning(f"Invalid phone number format: {phone_number}")
            return False, "Invalid phone number format (use E.164: 34612345678)"

        url = f"{WhatsAppMessageService.WHATSAPP_API_BASE_URL}/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }

        try:
            logger.info(f"Sending WhatsApp template '{template_name}' to {phone_number}")
            response = requests.post(url, json=payload, headers=headers, timeout=WhatsAppMessageService.REQUEST_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"Template message sent successfully. ID: {message_id}")
                return True, message_id

            elif response.status_code == 429:
                if retry_count < WhatsAppMessageService.MAX_RETRIES:
                    import time
                    logger.warning(f"Rate limited (429). Retrying... ({retry_count + 1}/{WhatsAppMessageService.MAX_RETRIES})")
                    time.sleep(WhatsAppMessageService.RETRY_DELAY_SECONDS)
                    return WhatsAppMessageService.send_template_message(
                        phone_number,
                        template_name,
                        language_code,
                        retry_count + 1
                    )
                else:
                    error = "Rate limited (429) - max retries exceeded"
                    logger.error(error)
                    return False, error

            elif response.status_code == 401:
                error = "Unauthorized - check WHATSAPP_ACCESS_TOKEN"
                logger.error(error)
                return False, error

            else:
                error = f"WhatsApp API error ({response.status_code}): {response.text}"
                logger.error(error)
                return False, error

        except requests.exceptions.Timeout:
            if retry_count < WhatsAppMessageService.MAX_RETRIES:
                import time
                logger.warning(f"Timeout. Retrying... ({retry_count + 1}/{WhatsAppMessageService.MAX_RETRIES})")
                time.sleep(WhatsAppMessageService.RETRY_DELAY_SECONDS)
                return WhatsAppMessageService.send_template_message(
                    phone_number,
                    template_name,
                    language_code,
                    retry_count + 1
                )
            else:
                error = "Request timeout - max retries exceeded"
                logger.error(error)
                return False, error

        except Exception as e:
            error = f"Unexpected error sending template: {str(e)}"
            logger.exception(error)
            return False, error
    
    @staticmethod
    def _is_valid_e164(phone_number: str) -> bool:
        """
        Valida que el teléfono esté en formato E.164.
        
        Formato válido: [1-9]{1,3}[0-9]{1,14}
        Ejemplos:
        - 34612345678 (España)
        - 5491123456789 (Argentina)
        - 12125552368 (USA)
        """
        import re
        pattern = r'^[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone_number))


__all__ = ["WhatsAppMessageService"]
