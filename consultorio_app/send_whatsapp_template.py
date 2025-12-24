import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app.services.whatsapp.whatsapp_message_service import WhatsAppMessageService

if __name__ == "__main__":
    # Número destino en E.164 sin '+' (ej: 5491123456789)
    to = os.environ.get("SANDBOX_TEST_TO") or input("Ingrese teléfono destino (E.164 sin '+'): ")
    template = os.environ.get("SANDBOX_TEMPLATE", "jaspers_market_plain_text_v1")
    language = os.environ.get("SANDBOX_TEMPLATE_LANG", "en_US")

    ok, result = WhatsAppMessageService.send_template_message(
        phone_number=to,
        template_name=template,
        language_code=language
    )

    if ok:
        print(f"[OK] Enviado. ID mensaje: {result}")
    else:
        print(f"[ERROR] {result}")
