"""
WhatsApp Webhook Handler.

Responsabilidades:
- Validar firma/token del webhook
- Parsear payload de WhatsApp
- Delegar al ConversationService
- Retornar respuesta HTTP
- NO contiene lógica de negocio (eso está en ConversationService)
"""

import hmac
import hashlib
import json
import os
from typing import Optional, Dict, Any, Tuple


class WhatsAppWebhookValidator:
    """Valida la firma del webhook de WhatsApp."""

    @staticmethod
    def validate_signature(
        body: str,
        signature_header: str,
        verify_token: str,  # mantenido por compatibilidad, no se usa para la firma
    ) -> bool:
        """
        Valida que la firma sea legítima usando HMAC-SHA256.

        Args:
            body: Raw body del request (string)
            signature_header: Header X-Hub-Signature-256 (ej: "sha256=...")
            verify_token: Token secreto configurado (de variable de entorno)

        Returns:
            True si firma es válida; False en caso contrario
        """
        # La firma X-Hub-Signature-256 se calcula con el App Secret de Meta, no con el verify_token
        app_secret = os.environ.get('META_APP_SECRET') or os.environ.get('WHATSAPP_APP_SECRET')
        is_dev = os.environ.get('FLASK_ENV', 'development') != 'production'

        # En desarrollo permitimos pasar sin firma para facilitar pruebas locales
        if not signature_header or not app_secret:
            return True if is_dev else False

        try:
            hash_algorithm, hash_value = signature_header.split('=', 1)
            if hash_algorithm != 'sha256':
                return False
        except (ValueError, IndexError):
            return False

        expected_hash = hmac.new(
            app_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(hash_value, expected_hash)


class WhatsAppPayloadParser:
    """Parsea payloads del webhook de WhatsApp."""

    @staticmethod
    def extract_message_info(payload: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """
        Extrae channel_user_id y texto del mensaje del payload.

        Returns:
            Tupla (channel_user_id, texto) o None si payload inválido
        """
        try:
            entry = payload.get('entry', [{}])[0]
            change = entry.get('changes', [{}])[0]
            value = change.get('value', {})
            messages = value.get('messages', [])

            if not messages:
                return None

            msg = messages[0]
            channel_user_id = msg.get('from')

            if msg.get('type') != 'text':
                return None

            text = msg.get('text', {}).get('body', '')

            if not channel_user_id or not text:
                return None

            return (channel_user_id, text)
        except (KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def is_status_update(payload: Dict[str, Any]) -> bool:
        """
        Detecta si el payload es una actualización de estado (no un mensaje).

        Returns:
            True si es update de estado; False si es mensaje
        """
        try:
            entry = payload.get('entry', [{}])[0]
            change = entry.get('changes', [{}])[0]
            value = change.get('value', {})
            return bool(value.get('statuses'))
        except (KeyError, IndexError, TypeError):
            return False


class WhatsAppMessageFormatter:
    """Formatea respuestas del ConversationService para WhatsApp."""

    @staticmethod
    def format_response(message: str, phone_number: str) -> Dict[str, Any]:
        """Formatea respuesta para enviar vía WhatsApp API."""
        return {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }

    @staticmethod
    def format_webhook_ack() -> Dict[str, Any]:
        """Retorna ACK para respuesta HTTP al webhook."""
        return {"status": "received"}


class WhatsAppWebhookHandler:
    """Handler principal del webhook. Orquesta validación, parsing y delegación."""

    def __init__(self, verify_token: str):
        self.verify_token = verify_token
        self.last_reply_message: Optional[str] = None

    def handle_webhook(
        self,
        body: str,
        signature_header: str,
        conversation_service,
    ) -> Tuple[Dict[str, Any], int]:
        """
        Procesa un webhook entrante y retorna (response_dict, status_code).
        """
        self.last_reply_message = None

        if not WhatsAppWebhookValidator.validate_signature(
            body,
            signature_header,
            self.verify_token,
        ):
            return ({"error": "Invalid signature"}, 401)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ({"error": "Invalid JSON"}, 400)

        if WhatsAppPayloadParser.is_status_update(payload):
            return (WhatsAppMessageFormatter.format_webhook_ack(), 200)

        message_info = WhatsAppPayloadParser.extract_message_info(payload)
        if not message_info:
            return (WhatsAppMessageFormatter.format_webhook_ack(), 200)

        channel_user_id, text = message_info

        try:
            reply = conversation_service.handle_message(channel_user_id, text)
            self.last_reply_message = getattr(reply, "message", None)
        except Exception:
            return ({"error": "Service error"}, 500)

        return (WhatsAppMessageFormatter.format_webhook_ack(), 200)

    @staticmethod
    def handle_challenge(verify_token_param: str, verify_token_secret: str) -> Tuple[str, int]:
        """Maneja el challenge inicial de WhatsApp (verificación de webhook)."""
        if verify_token_param == verify_token_secret:
            return ("OK", 200)
        else:
            return ("Forbidden", 403)
