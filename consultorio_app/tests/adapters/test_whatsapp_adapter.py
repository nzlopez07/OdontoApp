"""
Tests para WhatsApp adapter (validación de firma, parsing, etc).
"""

import json
import hmac
import hashlib
import pytest
from app.adapters.whatsapp.webhook_handler import (
    WhatsAppWebhookValidator,
    WhatsAppPayloadParser,
    WhatsAppWebhookHandler,
)


class MockConversationService:
    """Mock para ConversationService en tests."""
    
    def handle_message(self, channel_user_id, text):
        """Retorna una respuesta dummy."""
        from app.services.conversacion import ConversationReply
        return ConversationReply(
            message=f"Echo: {text}",
            step="test",
            done=False
        )


class TestWhatsAppWebhookValidator:
    """Tests para validación de firma HMAC."""
    
    def test_valid_signature(self):
        """Debe aceptar firma válida."""
        verify_token = "test-secret"
        body = '{"object":"whatsapp_business_account"}'
        
        # Computar firma correcta
        signature = "sha256=" + hmac.new(
            verify_token.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        result = WhatsAppWebhookValidator.validate_signature(
            body, signature, verify_token
        )
        assert result is True
    
    def test_invalid_signature(self):
        """Debe rechazar firma inválida."""
        verify_token = "test-secret"
        body = '{"object":"whatsapp_business_account"}'
        invalid_signature = "sha256=bad_hash_here"
        
        result = WhatsAppWebhookValidator.validate_signature(
            body, invalid_signature, verify_token
        )
        assert result is False
    
    def test_no_verify_token(self):
        """Debe rechazar si no hay token configurado."""
        body = '{"object":"whatsapp_business_account"}'
        signature = "sha256=any_hash"
        
        result = WhatsAppWebhookValidator.validate_signature(
            body, signature, ""
        )
        assert result is False
    
    def test_malformed_signature_header(self):
        """Debe rechazar header malformado."""
        verify_token = "test-secret"
        body = '{"object":"whatsapp_business_account"}'
        
        # Sin "sha256=" prefix
        result = WhatsAppWebhookValidator.validate_signature(
            body, "bad_format", verify_token
        )
        assert result is False
    
    def test_wrong_algorithm(self):
        """Debe rechazar algoritmo incorrecto."""
        verify_token = "test-secret"
        body = '{"object":"whatsapp_business_account"}'
        
        # sha256 pero header dice md5
        signature = "md5=" + hmac.new(
            verify_token.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        result = WhatsAppWebhookValidator.validate_signature(
            body, signature, verify_token
        )
        assert result is False


class TestWhatsAppPayloadParser:
    """Tests para parsing de payloads."""
    
    def test_extract_message_info_valid(self):
        """Debe extraer channel_user_id y texto."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "34612345678",
                                        "type": "text",
                                        "text": {"body": "Hola doctora"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = WhatsAppPayloadParser.extract_message_info(payload)
        assert result == ("34612345678", "Hola doctora")
    
    def test_extract_message_info_no_messages(self):
        """Debe retornar None si no hay mensajes."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": []
                            }
                        }
                    ]
                }
            ]
        }
        
        result = WhatsAppPayloadParser.extract_message_info(payload)
        assert result is None
    
    def test_extract_message_info_non_text_type(self):
        """Debe retornar None para mensajes no-texto."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "34612345678",
                                        "type": "image",
                                        "image": {"id": "123"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = WhatsAppPayloadParser.extract_message_info(payload)
        assert result is None
    
    def test_extract_message_info_empty_text(self):
        """Debe retornar None si el texto está vacío."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "34612345678",
                                        "type": "text",
                                        "text": {"body": ""}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = WhatsAppPayloadParser.extract_message_info(payload)
        assert result is None
    
    def test_is_status_update_true(self):
        """Debe detectar updates de estado."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "msg_id",
                                        "status": "delivered"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = WhatsAppPayloadParser.is_status_update(payload)
        assert result is True
    
    def test_is_status_update_false(self):
        """Debe retornar False para mensajes."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "34612345678",
                                        "type": "text",
                                        "text": {"body": "Hola"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = WhatsAppPayloadParser.is_status_update(payload)
        assert result is False


class TestWhatsAppWebhookHandler:
    """Tests para handler completo."""
    
    def test_handle_webhook_invalid_signature(self):
        """Debe rechazar webhook con firma inválida."""
        handler = WhatsAppWebhookHandler("test-secret")
        body = '{"object":"whatsapp_business_account"}'
        invalid_sig = "sha256=bad"
        
        response, status = handler.handle_webhook(
            body,
            invalid_sig,
            MockConversationService()
        )
        
        assert status == 401
        assert "error" in response
    
    def test_handle_webhook_valid_message(self):
        """Debe procesar mensaje válido."""
        handler = WhatsAppWebhookHandler("test-secret")
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "34612345678",
                                        "type": "text",
                                        "text": {"body": "Hola"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        body = json.dumps(payload)
        
        # Computar firma válida
        signature = "sha256=" + hmac.new(
            b"test-secret",
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        response, status = handler.handle_webhook(
            body,
            signature,
            MockConversationService()
        )
        
        assert status == 200
        assert response.get("status") == "received"
    
    def test_handle_webhook_status_update(self):
        """Debe ignorar updates de estado."""
        handler = WhatsAppWebhookHandler("test-secret")
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "msg_id",
                                        "status": "delivered"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        body = json.dumps(payload)
        
        signature = "sha256=" + hmac.new(
            b"test-secret",
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        response, status = handler.handle_webhook(
            body,
            signature,
            MockConversationService()
        )
        
        assert status == 200
        assert response.get("status") == "received"
    
    def test_handle_webhook_invalid_json(self):
        """Debe rechazar JSON malformado."""
        handler = WhatsAppWebhookHandler("test-secret")
        body = "not-valid-json"
        
        signature = "sha256=" + hmac.new(
            b"test-secret",
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        response, status = handler.handle_webhook(
            body,
            signature,
            MockConversationService()
        )
        
        assert status == 400
        assert "error" in response
    
    def test_handle_challenge(self):
        """Debe procesar challenge inicial."""
        verify_token = "test-secret"
        
        # Token correcto
        response, status = WhatsAppWebhookHandler.handle_challenge(
            "test-secret",
            verify_token
        )
        assert status == 200
        
        # Token incorrecto
        response, status = WhatsAppWebhookHandler.handle_challenge(
            "wrong-token",
            verify_token
        )
        assert status == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
