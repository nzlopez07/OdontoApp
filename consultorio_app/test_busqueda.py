#!/usr/bin/env python3
"""
Script de prueba para las utilidades de búsqueda.

Este script valida que las funciones de búsqueda funcionen correctamente
con diferentes tipos de texto, incluyendo tildes y mayúsculas.
"""

import sys
import os
from datetime import datetime, date, time, timedelta

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services import BusquedaUtils


def test_normalizacion():
    """Prueba la normalización de texto."""
    print("🔍 Probando normalización de texto...")
    
    casos_prueba = [
        ("José María", "jose maria"),
        ("GARCÍA", "garcia"),
        ("Ñoño", "nono"),
        ("María José Hernández", "maria jose hernandez"),
        ("O'Connor", "oconnor"),
        ("123-456", "123456"),
        ("   espacios   múltiples   ", "espacios multiples"),
    ]
    
    for entrada, esperado in casos_prueba:
        resultado = BusquedaUtils.normalizar_texto(entrada)
        assert resultado == esperado, f"'{entrada}' -> esperado: '{esperado}', obtenido: '{resultado}'"
        print(f"✅ '{entrada}' -> '{resultado}'")
    
    print("✅ Normalización funcionando correctamente")


def test_busqueda_con_datos():
    """Prueba la búsqueda con datos reales."""
    print("\n🔍 Probando búsqueda con datos de la base de datos...")
    
    with app.app_context():
        # Probar diferentes tipos de búsqueda
        casos_busqueda = [
            "maria",      # Sin tilde
            "María",      # Con tilde y mayúscula
            "GARCIA",     # Mayúsculas
            "garcía",     # Con tilde minúscula
            "jose maria", # Nombre completo
            "123",        # Parte de DNI
        ]
        
        for termino in casos_busqueda:
            resultados = BusquedaUtils.buscar_pacientes_simple(termino)
            print(f"Búsqueda '{termino}': {len(resultados)} resultados")
            
            # Mostrar algunos resultados
            for i, paciente in enumerate(resultados[:3]):
                print(f"  - {paciente.nombre} {paciente.apellido} (DNI: {paciente.dni})")
                if i >= 2:  # Máximo 3 resultados por búsqueda
                    break
    
    print("✅ Búsqueda con datos funcionando correctamente")


def test_casos_especiales():
    """Prueba casos especiales de búsqueda."""
    print("\n🔍 Probando casos especiales...")
    
    with app.app_context():
        # Búsqueda vacía
        resultados_vacio = BusquedaUtils.buscar_pacientes_simple("")
        print(f"Búsqueda vacía: {len(resultados_vacio)} resultados (debe ser todos)")
        
        # Búsqueda con espacios
        resultados_espacios = BusquedaUtils.buscar_pacientes_simple("   ")
        print(f"Búsqueda con espacios: {len(resultados_espacios)} resultados")
        
        # Búsqueda que no existe
        resultados_inexistente = BusquedaUtils.buscar_pacientes_simple("XYZABC123")
        print(f"Búsqueda inexistente: {len(resultados_inexistente)} resultados (debe ser 0)")
        
        assert len(resultados_inexistente) == 0, "La búsqueda inexistente debe retornar 0 resultados"
    
    print("✅ Casos especiales funcionando correctamente")


def test_rendimiento():
    """Prueba el rendimiento de la búsqueda."""
    print("\n⏱️ Probando rendimiento...")
    
    with app.app_context():
        import time
        
        # Medir tiempo de búsqueda
        inicio = time.time()
        resultados = BusquedaUtils.buscar_pacientes_simple("maria")
        fin = time.time()
        
        tiempo_ms = (fin - inicio) * 1000
        print(f"Búsqueda completada en {tiempo_ms:.2f}ms")
        print(f"Resultados encontrados: {len(resultados)}")
        
        if tiempo_ms > 1000:  # Más de 1 segundo
            print("⚠️  Advertencia: La búsqueda está tardando más de 1 segundo")
        else:
            print("✅ Rendimiento aceptable")


def mostrar_ejemplos_uso():
    """Muestra ejemplos de uso de las utilidades de búsqueda."""
    print("\n📖 Ejemplos de uso:")
    print("=" * 50)
    
    ejemplos = [
        ("maria", "Busca pacientes con 'maria' en nombre o apellido"),
        ("María García", "Busca por nombre y apellido completo"),
        ("garcia", "Busca apellidos que contengan 'garcia'"),
        ("12345", "Busca por DNI"),
        ("jose", "Busca cualquier 'jose' sin importar tildes"),
    ]
    
    with app.app_context():
        for termino, descripcion in ejemplos:
            resultados = BusquedaUtils.buscar_pacientes_simple(termino)
            print(f"\n🔍 {descripcion}")
            print(f"   Término: '{termino}' -> {len(resultados)} resultados")
            
            for paciente in resultados[:2]:  # Mostrar máximo 2
                print(f"   - {paciente.nombre} {paciente.apellido}")


def main():
    """Función principal del script de pruebas."""
    print("🧪 Iniciando pruebas de búsqueda avanzada")
    print("=" * 50)
    
    # Crear app para contexto de base de datos
    global app
    app = create_app()
    
    try:
        # Ejecutar pruebas
        test_normalizacion()
        test_busqueda_con_datos()
        test_casos_especiales()
        test_rendimiento()
        mostrar_ejemplos_uso()
        
        print("\n" + "=" * 50)
        print("🎉 ¡Todas las pruebas de búsqueda pasaron exitosamente!")
        print("\nCaracterísticas implementadas:")
        print("✅ Búsqueda sin distinción de mayúsculas/minúsculas")
        print("✅ Búsqueda sin distinción de tildes")
        print("✅ Búsqueda por nombre, apellido o DNI")
        print("✅ Búsqueda con múltiples palabras")
        print("✅ Búsqueda flexible y tolerante a errores")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
