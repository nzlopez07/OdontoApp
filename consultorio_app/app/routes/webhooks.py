"""
Rutas para webhooks (WhatsApp, etc).
"""

from flask import Blueprint, request, current_app, jsonify
from app.adapters.whatsapp import WhatsAppWebhookHandler
from app.services import ConversationService
from app.services.whatsapp import WhatsAppMessageService
from app.security import RateLimiter
import os
import logging

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')
logger = logging.getLogger(__name__)


@webhooks_bp.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """
    Webhook para mensajes y eventos de WhatsApp.
    
    GET: Verificación inicial (challenge) de WhatsApp.
    POST: Mensajes y actualizaciones de estado.
    """
    verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', '')
    
    if request.method == 'GET':
        # Challenge inicial
        hub_mode = request.args.get('hub.mode')
        hub_verify_token = request.args.get('hub.verify_token')
        hub_challenge = request.args.get('hub.challenge')
        
        if hub_mode == 'subscribe':
            response_text, status = WhatsAppWebhookHandler.handle_challenge(
                hub_verify_token,
                verify_token
            )
            if status == 200 and hub_challenge:
                return hub_challenge, status
            else:
                return response_text, status
        else:
            return "Invalid request", 400
    
    elif request.method == 'POST':
        # Procesar webhook
        body = request.get_data(as_text=True)
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # Log de entrada
        logger.debug(f"Webhook received from {request.remote_addr}")
        
        handler = WhatsAppWebhookHandler(verify_token)
        response_data, status = handler.handle_webhook(
            body,
            signature,
            ConversationService
        )
        
        # Si la respuesta fue procesada exitosamente, intentar enviar mensaje
        if status == 200 and response_data.get('status') == 'received' and getattr(handler, 'last_reply_message', None):
            try:
                # Extraer información del webhook
                import json
                payload = json.loads(body)
                
                # Información del mensaje
                from app.adapters.whatsapp.webhook_handler import WhatsAppPayloadParser
                message_info = WhatsAppPayloadParser.extract_message_info(payload)
                
                if message_info:
                    channel_user_id, _ = message_info
                    
                    # Verificar rate limit
                    allowed, limit_message = RateLimiter.check_rate_limit(channel_user_id)
                    if not allowed:
                        logger.warning(f"Rate limit exceeded for {channel_user_id}")
                        # El rate limit se debe aplicar antes de procesar, 
                        # pero por ahora solo lo logueamos
                    
                    # Enviar respuesta vía WhatsApp (reply_message ya contiene el texto)
                    success, result = WhatsAppMessageService.send_text_message(
                        channel_user_id,
                        handler.last_reply_message
                    )
                    
                    if success:
                        logger.info(f"Message sent successfully to {channel_user_id}")
                    else:
                        logger.error(f"Failed to send message to {channel_user_id}: {result}")
            
            except Exception as e:
                logger.exception(f"Error sending WhatsApp message: {str(e)}")
                # No fallar el webhook por error en envío
        
        return jsonify(response_data), status
    
    return "Method not allowed", 405

