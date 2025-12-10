#!/usr/bin/env python3
"""
Script de pruebas para validar el funcionamiento de la base de datos
y los modelos del Sistema de Gestión de Consultorio Odontológico.
"""

import sys
import os
from datetime import datetime, date, time

# Agregar los directorios necesarios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.database import db
from app.database.utils import init_database
from app.models import (
    Paciente, Turno, Estado, CambioEstado, 
    Localidad, ObraSocial, Operacion, Codigo
)

def test_database_operations():
    """Prueba las operaciones básicas de la base de datos"""
    print("🧪 PRUEBAS DE OPERACIONES DE BASE DE DATOS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Crear tablas
        print("1. Probando creación de tablas...")
        db.create_all()
        print("   ✅ Tablas creadas correctamente")
        
        # Test 2: Insertar y consultar estado
        print("2. Probando inserción y consulta de Estado...")
        estado_test = Estado(nombre="Test_Estado")
        db.session.add(estado_test)
        db.session.commit()
        
        estado_consultado = Estado.query.filter_by(nombre="Test_Estado").first()
        assert estado_consultado is not None, "Error: No se pudo consultar el estado"
        print(f"   ✅ Estado insertado y consultado: {estado_consultado.nombre}")
        
        # Test 3: Insertar paciente con relaciones
        print("3. Probando inserción de Paciente con relaciones...")
        paciente_test = Paciente(
            nombre="Test",
            apellido="Usuario",
            dni="99999999",
            fecha_nac=date(1990, 1, 1),
            telefono="999999999",
            direccion="Calle Test 123"
        )
        db.session.add(paciente_test)
        db.session.commit()
        
        paciente_consultado = Paciente.query.filter_by(dni="99999999").first()
        assert paciente_consultado is not None, "Error: No se pudo consultar el paciente"
        print(f"   ✅ Paciente insertado: {paciente_consultado.nombre} {paciente_consultado.apellido}")
        
        # Test 4: Crear turno y verificar relación
        print("4. Probando relación Paciente-Turno...")
        turno_test = Turno(
            fecha=date(2025, 12, 31),
            hora=time(15, 30),
            paciente_id=paciente_consultado.id,
            detalle="Turno de prueba"
        )
        db.session.add(turno_test)
        db.session.commit()
        
        # Verificar relación
        turnos_paciente = paciente_consultado.turnos
        assert len(turnos_paciente) > 0, "Error: Relación Paciente-Turno no funciona"
        print(f"   ✅ Relación verificada: Paciente tiene {len(turnos_paciente)} turno(s)")
        
        # Test 5: Crear código y operación
        print("5. Probando relación Operación-Código...")
        codigo_test = Codigo(numero="999", descripcion="Código de prueba")
        db.session.add(codigo_test)
        db.session.commit()
        
        operacion_test = Operacion(
            paciente_id=paciente_consultado.id,
            descripcion="Operación de prueba",
            monto=1000.0,
            fecha=datetime.now(),
            codigo_id=codigo_test.id
        )
        db.session.add(operacion_test)
        db.session.commit()
        
        # Verificar relación
        assert operacion_test.codigo is not None, "Error: Relación Operación-Código no funciona"
        print(f"   ✅ Operación creada con código: {operacion_test.codigo.numero}")
        
        # Limpiar datos de prueba
        print("6. Limpiando datos de prueba...")
        db.session.delete(operacion_test)
        db.session.delete(codigo_test)
        db.session.delete(turno_test)
        db.session.delete(paciente_test)
        db.session.delete(estado_test)
        db.session.commit()
        print("   ✅ Datos de prueba eliminados")
        
        print("\n🎉 TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        return True

def test_edge_cases():
    """Prueba casos extremos y validaciones"""
    print("\n🔍 PRUEBAS DE CASOS EXTREMOS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test de unicidad en Estado
        print("1. Probando restricción UNIQUE en Estado...")
        try:
            estado1 = Estado(nombre="Estado_Unico")
            estado2 = Estado(nombre="Estado_Unico")  # Mismo nombre
            db.session.add(estado1)
            db.session.add(estado2)
            db.session.commit()
            print("   ❌ Error: Se permitió duplicar estado")
            return False
        except Exception:
            db.session.rollback()
            print("   ✅ Restricción UNIQUE funcionando correctamente")
        
        print("\n🎉 PRUEBAS DE CASOS EXTREMOS COMPLETADAS")
        return True

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        success1 = test_database_operations()
        success2 = test_edge_cases()
        
        if success1 and success2:
            print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            return True
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LAS PRUEBAS: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
