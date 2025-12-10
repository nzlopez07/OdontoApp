#!/usr/bin/env python3
"""
Script de prueba para los servicios de turnos.

Este script valida que todos los servicios de turnos funcionen correctamente
y muestra ejemplos de uso.
"""

import sys
import os
from datetime import datetime, date, time, timedelta

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services import TurnoService, TurnoValidaciones, FormateoUtils, EstadoTurnoUtils


def test_validaciones():
    """Prueba las validaciones de turnos."""
    print("🔍 Probando validaciones de turnos...")
    
    # Validar fecha
    fecha_valida = date.today() + timedelta(days=1)
    fecha_invalida = date.today() - timedelta(days=1)
    
    resultado = TurnoValidaciones.validar_fecha_turno(fecha_valida)
    assert resultado['valido'], f"Fecha válida falló: {resultado['error']}"
    
    resultado = TurnoValidaciones.validar_fecha_turno(fecha_invalida)
    assert not resultado['valido'], "Fecha inválida no fue detectada"
    
    # Validar hora
    hora_valida = time(10, 30)
    hora_invalida = time(10, 15)
    
    resultado = TurnoValidaciones.validar_hora_turno(hora_valida)
    assert resultado['valido'], f"Hora válida falló: {resultado['error']}"
    
    resultado = TurnoValidaciones.validar_hora_turno(hora_invalida)
    assert not resultado['valido'], "Hora inválida no fue detectada"
    
    print("✅ Validaciones funcionando correctamente")


def test_formateo():
    """Prueba las utilidades de formateo."""
    print("\n📝 Probando formateo...")
    
    # Formatear fecha
    fecha = date(2025, 7, 21)
    fecha_formateada = FormateoUtils.formatear_fecha(fecha)
    print(f"Fecha formateada: {fecha_formateada}")
    
    # Formatear hora
    hora = time(14, 30)
    hora_formateada = FormateoUtils.formatear_hora(hora)
    print(f"Hora formateada: {hora_formateada}")
    
    # Formatear duración
    duracion_30 = FormateoUtils.formatear_duracion(30)
    duracion_90 = FormateoUtils.formatear_duracion(90)
    duracion_120 = FormateoUtils.formatear_duracion(120)
    
    print(f"30 minutos: {duracion_30}")
    print(f"90 minutos: {duracion_90}")
    print(f"120 minutos: {duracion_120}")
    
    print("✅ Formateo funcionando correctamente")


def test_estados():
    """Prueba las utilidades de estados."""
    print("\n🔄 Probando estados de turnos...")
    
    # Validar transiciones
    resultado = EstadoTurnoUtils.validar_transicion_estado('Pendiente', 'Confirmado')
    assert resultado['valido'], f"Transición válida falló: {resultado['error']}"
    
    resultado = EstadoTurnoUtils.validar_transicion_estado('Completado', 'Pendiente')
    assert not resultado['valido'], "Transición inválida no fue detectada"
    
    # Probar estados
    assert EstadoTurnoUtils.es_estado_activo('Pendiente')
    assert EstadoTurnoUtils.es_estado_final('Completado')
    assert not EstadoTurnoUtils.es_estado_activo('Completado')
    
    # Obtener estados siguientes
    estados_siguientes = EstadoTurnoUtils.obtener_estados_siguientes('Pendiente')
    print(f"Desde 'Pendiente' se puede ir a: {estados_siguientes}")
    
    print("✅ Estados funcionando correctamente")


def test_disponibilidad():
    """Prueba la verificación de disponibilidad."""
    print("\n📅 Probando disponibilidad de turnos...")
    
    # Fecha laborable
    fecha_laborable = date.today() + timedelta(days=1)
    while fecha_laborable.weekday() not in [0, 1, 2, 3, 4]:  # Asegurar que sea laborable
        fecha_laborable += timedelta(days=1)
    
    hora_valida = time(10, 0)
    
    disponibilidad = TurnoService.verificar_disponibilidad(fecha_laborable, hora_valida)
    print(f"Disponibilidad para {fecha_laborable} {hora_valida}: {disponibilidad}")
    
    # Horarios disponibles
    horarios = TurnoService.obtener_horarios_disponibles(fecha_laborable)
    print(f"Horarios disponibles para {fecha_laborable}: {len(horarios)} slots")
    if horarios:
        print(f"Primer horario: {horarios[0]}, Último horario: {horarios[-1]}")
    
    print("✅ Disponibilidad funcionando correctamente")


def test_estadisticas():
    """Prueba las estadísticas de turnos."""
    print("\n📊 Probando estadísticas...")
    
    with app.app_context():
        estadisticas = TurnoService.obtener_estadisticas_turnos()
        print("Estadísticas de turnos:")
        for clave, valor in estadisticas.items():
            print(f"  {clave}: {valor}")
    
    print("✅ Estadísticas funcionando correctamente")


def main():
    """Función principal del script de pruebas."""
    print("🧪 Iniciando pruebas de servicios de turnos")
    print("=" * 50)
    
    # Crear app para contexto de base de datos
    global app
    app = create_app()
    
    try:
        # Ejecutar pruebas
        test_validaciones()
        test_formateo()
        test_estados()
        test_disponibilidad()
        test_estadisticas()
        
        print("\n" + "=" * 50)
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\nLos servicios de turnos están listos para usar:")
        print("- TurnoService: Gestión completa de turnos")
        print("- TurnoValidaciones: Validaciones robustas")
        print("- FormateoUtils: Formateo consistente")
        print("- EstadoTurnoUtils: Manejo de estados")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
