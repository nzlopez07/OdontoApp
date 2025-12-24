#!/usr/bin/env python3
"""
Script de testing local para WhatsApp (sin API real).

Simula conversación completa con el bot sin necesidad de tokens de Meta.

Uso:
    python test_whatsapp_local.py
    LOG_LEVEL=DEBUG python test_whatsapp_local.py
"""

import json
import hmac
import hashlib
import sys
import os
from datetime import date, timedelta

# Agregar path para importar app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
import app.models  # CRITICAL: Importar TODOS los modelos ANTES de db.create_all()

# Configurar app
app = create_app()

# Context para tests
app_context = app.app_context()
app_context.push()

# Variables de test
import random
import string
VERIFY_TOKEN = "test-secret"  # Token que usamos en test

# Generar teléfono pseudoaleatorio por ejecución para evitar conversaciones previas
TEST_PHONE = "346" + "".join(random.choice(string.digits) for _ in range(8))

# DNI y nombres aleatorios por ejecución
TEST_DNI = str(random.randint(20000000, 99000000))
FIRST_NAMES = [
    "Juan", "Ana", "Luis", "Sofía", "María", "Pedro", "Lucía", "Diego",
    "Valentina", "Martín", "Camila", "Nicolás", "Carla", "Mateo"
]
LAST_NAMES = [
    "García", "López", "Pérez", "Martínez", "Gómez", "Fernández", "Díaz",
    "Rodríguez", "Sánchez", "Romero", "Herrera", "Castro"
]
TEST_NOMBRE = random.choice(FIRST_NAMES)
TEST_APELLIDO = random.choice(LAST_NAMES)


def make_webhook_payload(phone: str, message: str) -> str:
    """Crea un payload válido de WhatsApp."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "text",
                        "text": {"body": message}
                    }]
                }
            }]
        }]
    }
    return json.dumps(payload)


def make_signature(body: str, token: str) -> str:
    """Genera firma HMAC-SHA256 válida."""
    return "sha256=" + hmac.new(
        token.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def send_message(message_text: str, phone: str = TEST_PHONE) -> tuple:
    """Envía un mensaje simulado al webhook."""
    body = make_webhook_payload(phone, message_text)
    signature = make_signature(body, VERIFY_TOKEN)
    
    print(f"   [DEBUG] Enviando: '{message_text}' a {phone}")
    
    with app.test_client() as client:
        response = client.post(
            '/webhooks/whatsapp',
            data=body,
            headers={
                'X-Hub-Signature-256': signature,
                'Content-Type': 'application/json'
            }
        )
    
    # Inspeccionar conversación después del mensaje
    from app.services import ConversationService
    from app.models import Conversation
    convo = Conversation.query.filter_by(channel_user_id=phone).first()
    if convo:
        print(f"   [DEBUG] Conversation state: paso={convo.paso_actual}, nombre_tmp={convo.nombre_tmp}, apellido_tmp={convo.apellido_tmp}")
    
    return response.status_code, response.get_json()


def print_result(step: str, message: str, status: int, response: dict):
    """Imprime resultado de forma amigable."""
    status_icon = "[OK]" if status == 200 else "[FAIL]"
    print(f"\n{status_icon} Paso {step}: {message}")
    print(f"   Status: {status}")
    if response:
        print(f"   Response: {response}")


def main():
    """Ejecuta conversación completa de test."""
    print("=" * 70)
    print("Testing WhatsApp Integration (Local)")
    print("=" * 70)
    print(f"\nTesteando con teléfono: {TEST_PHONE}")
    print(f"Verify Token: {VERIFY_TOKEN}")
    print(f"Database: {os.environ.get('DATABASE_URL', 'sqlite:///consultorio.db')}\n")
    
    # DB nueva, no necesita reset
    
    # Test 1: Mensaje inicial con DNI
    print("\n" + "-" * 70)
    print("TEST 1: Enviar DNI")
    print("-" * 70)
    status, resp = send_message(TEST_DNI)
    print_result("1", f"Enviando DNI '{TEST_DNI}'", status, resp)
    
    # El usuario debería recibir: "No encontré tu ficha. Decime tu nombre para registrarte."
    expected_message = "No encontré" if status == 200 else None
    if status == 200:
        print("   [OK] Conversación iniciada - Pidiendo nombre")
    
    # Test 2: Enviar nombre
    print("\n" + "-" * 70)
    print("TEST 2: Enviar nombre")
    print("-" * 70)
    status, resp = send_message(TEST_NOMBRE)
    print_result("2", f"Enviando nombre '{TEST_NOMBRE}'", status, resp)
    if status == 200:
        print("   [OK] Nombre registrado - Pidiendo apellido")
    
    # Test 3: Enviar apellido
    print("\n" + "-" * 70)
    print("TEST 3: Enviar apellido")
    print("-" * 70)
    status, resp = send_message(TEST_APELLIDO)
    print_result("3", f"Enviando apellido '{TEST_APELLIDO}'", status, resp)
    if status == 200:
        print("   [OK] Paciente registrado - Pidiendo fecha")
    
    # Test 4: Enviar fecha válida (próximo día laborable futuro)
    print("\n" + "-" * 70)
    print("TEST 4: Enviar fecha")
    print("-" * 70)
    # Calcular próxima fecha laborable (Lun-Sáb) al menos 3 días en el futuro
    target = date.today() + timedelta(days=3)
    while target.weekday() > 5:  # 0-5 laborables, 6 domingo
        target += timedelta(days=1)
    target_str = target.strftime("%Y-%m-%d")
    status, resp = send_message(target_str)
    print_result("4", f"Enviando fecha '{target_str}'", status, resp)
    if status == 200:
        print("   [OK] Fecha aceptada - Pidiendo hora")
    
    # Test 5: Enviar hora válida
    print("\n" + "-" * 70)
    print("TEST 5: Enviar hora")
    print("-" * 70)
    status, resp = send_message("14:30")
    print_result("5", "Enviando hora '14:30'", status, resp)
    if status == 200:
        print("   [OK] Turno creado - Conversación completada")
    
    # Verificar que el turno fue creado
    print("\n" + "-" * 70)
    print("VERIFICACION: Turno creado en BD")
    print("-" * 70)
    try:
        from app.models import Turno, Paciente
        paciente = Paciente.query.filter_by(dni=TEST_DNI).first()
        if paciente:
            print(f"[OK] Paciente encontrado:")
            print(f"   - ID: {paciente.id}")
            print(f"   - Nombre: {paciente.nombre} {paciente.apellido}")
            print(f"   - DNI: {paciente.dni}")
            
            turnos = Turno.query.filter_by(paciente_id=paciente.id).all()
            if turnos:
                for turno in turnos:
                    print(f"[OK] Turno encontrado:")
                    print(f"   - ID: {turno.id}")
                    print(f"   - Fecha: {turno.fecha}")
                    print(f"   - Hora: {turno.hora}")
                    print(f"   - Estado: {turno.estado}")
                    print(f"   - Duracion: {turno.duracion} min")
            else:
                print("[FAIL] Turno no encontrado")
                # Mostrar TODOS los turnos para debugging
                todos_turnos = Turno.query.all()
                print(f"   [DEBUG] Total turnos en BD: {len(todos_turnos)}")
                for t in todos_turnos:
                    print(f"      - Turno {t.id}: paciente_id={t.paciente_id}, estado={t.estado}")
        else:
            print("[FAIL] Paciente no encontrado")
    except Exception as e:
        print(f"[FAIL] Error verificando BD: {str(e)}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("[OK] Testing completado")
    print("=" * 70)
    print("""
Próximos pasos:
1. Revisar logs: tail -f logs/whatsapp.log (si LOG_DIR está configurado)
2. Inspeccionar BD: sqlite3 instance/consultorio.db ".tables"
3. Limpiar y reintentar: python -c "from app.services import ConversationService; ConversationService.reset('34612345678')"
4. Para testing con números reales: ver docs/TESTING_WHATSAPP_PERSONAL.md
    """)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] Error durante testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        app_context.pop()
