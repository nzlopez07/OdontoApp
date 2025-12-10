#!/usr/bin/env python3
"""
Script de inicialización general del Sistema de Gestión de Consultorio Odontológico
Este script prueba todos los componentes principales del sistema.
"""

import sys
import os
from datetime import datetime, date, time

# Agregar los directorios necesarios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

# Imports principales
from app import create_app
from app.database import db
from app.database.utils import (
    init_database, backup_database, list_backups, 
    reset_database, get_session
)
from app.models import (
    Paciente, Turno, Estado, CambioEstado, 
    Localidad, ObraSocial, Operacion, Codigo
)

def print_header(title):
    """Imprime un header formateado"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    """Imprime un paso numerado"""
    print(f"\n{step_num}. {description}")

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"   ✅ {message}")

def print_info(message):
    """Imprime información"""
    print(f"   ℹ️  {message}")

def test_database_config():
    """Prueba la configuración de la base de datos"""
    print_header("PRUEBA DE CONFIGURACIÓN DE BASE DE DATOS")
    
    print_step(1, "Creando aplicación Flask")
    app = create_app()
    print_success("Aplicación Flask creada correctamente")
    
    print_step(2, "Verificando contexto de aplicación")
    with app.app_context():
        print_success("Contexto de aplicación inicializado")
        
        print_step(3, "Inicializando base de datos")
        init_database()
        
        print_step(4, "Verificando conexión a la base de datos")
        session = get_session()
        print_success(f"Sesión de base de datos: {type(session).__name__}")
        
    return app

def populate_sample_data(app):
    """Llena la base de datos con datos de ejemplo"""
    print_header("POBLACIÓN DE DATOS DE EJEMPLO")
    
    with app.app_context():
        print_step(1, "Creando estados básicos")
        estados_data = [
            "Pendiente", "Confirmado", "En curso", "Completado", 
            "Cancelado", "Reprogramado", "No asistió"
        ]
        
        for estado_nombre in estados_data:
            estado_existe = Estado.query.filter_by(nombre=estado_nombre).first()
            if not estado_existe:
                estado = Estado(nombre=estado_nombre)
                db.session.add(estado)
        db.session.commit()
        print_success(f"Estados creados: {len(estados_data)}")
        
        print_step(2, "Creando localidades")
        localidades_data = [
            "Buenos Aires", "Córdoba", "Rosario", "Mendoza", 
            "La Plata", "San Miguel de Tucumán"
        ]
        
        for localidad_nombre in localidades_data:
            localidad_existe = Localidad.query.filter_by(nombre=localidad_nombre).first()
            if not localidad_existe:
                localidad = Localidad(nombre=localidad_nombre)
                db.session.add(localidad)
        db.session.commit()
        print_success(f"Localidades creadas: {len(localidades_data)}")
        
        print_step(3, "Creando obras sociales")
        obras_sociales_data = [
            ("OSDE", "OS001"), ("Swiss Medical", "SM002"), 
            ("Galeno", "GL003"), ("IOMA", "IO004"), 
            ("Particular", None)
        ]
        
        for nombre, codigo in obras_sociales_data:
            obra_existe = ObraSocial.query.filter_by(nombre=nombre).first()
            if not obra_existe:
                obra = ObraSocial(nombre=nombre, codigo=codigo)
                db.session.add(obra)
        db.session.commit()
        print_success(f"Obras sociales creadas: {len(obras_sociales_data)}")
        
        print_step(4, "Creando códigos de operaciones")
        codigos_data = [
            ("001", "Consulta general"),
            ("002", "Limpieza dental"),
            ("003", "Empaste"),
            ("004", "Extracción"),
            ("005", "Endodoncia"),
            ("006", "Ortodoncia"),
            ("007", "Implante dental")
        ]
        
        for numero, descripcion in codigos_data:
            codigo_existe = Codigo.query.filter_by(numero=numero).first()
            if not codigo_existe:
                codigo = Codigo(numero=numero, descripcion=descripcion)
                db.session.add(codigo)
        db.session.commit()
        print_success(f"Códigos de operación creados: {len(codigos_data)}")

def create_sample_patients(app):
    """Crea pacientes de ejemplo"""
    print_header("CREACIÓN DE PACIENTES DE EJEMPLO")
    
    with app.app_context():
        # Obtener datos relacionados
        localidad = Localidad.query.first()
        obra_social = ObraSocial.query.first()
        
        pacientes_data = [
            {
                "nombre": "Juan", "apellido": "Pérez", "dni": "12345678",
                "fecha_nac": date(1985, 3, 15), "telefono": "1123456789",
                "direccion": "Av. Corrientes 1234", "barrio": "Centro"
            },
            {
                "nombre": "María", "apellido": "González", "dni": "87654321",
                "fecha_nac": date(1992, 7, 22), "telefono": "1187654321",
                "direccion": "Calle Florida 567", "barrio": "Palermo"
            },
            {
                "nombre": "Carlos", "apellido": "López", "dni": "11223344",
                "fecha_nac": date(1978, 11, 8), "telefono": "1111223344",
                "direccion": "Av. Santa Fe 890", "barrio": "Recoleta"
            }
        ]
        
        pacientes_creados = 0
        for i, datos in enumerate(pacientes_data, 1):
            paciente_existe = Paciente.query.filter_by(dni=datos["dni"]).first()
            if not paciente_existe:
                paciente = Paciente(
                    **datos,
                    localidad_id=localidad.id if localidad else None,
                    obra_social_id=obra_social.id if obra_social else None,
                    carnet="12345" if obra_social else None,
                    titular="Titular" if obra_social else None,
                    parentesco="Titular" if obra_social else None
                )
                db.session.add(paciente)
                pacientes_creados += 1
                print_step(i, f"Paciente creado: {datos['nombre']} {datos['apellido']}")
        
        db.session.commit()
        print_success(f"Total de pacientes creados: {pacientes_creados}")

def create_sample_appointments(app):
    """Crea turnos de ejemplo"""
    print_header("CREACIÓN DE TURNOS DE EJEMPLO")
    
    with app.app_context():
        pacientes = Paciente.query.all()
        estados = Estado.query.all()
        
        if not pacientes or not estados:
            print("⚠️  No hay pacientes o estados disponibles")
            return
        
        turnos_data = [
            {"fecha": date(2025, 8, 1), "hora": time(9, 0), "detalle": "Consulta de rutina"},
            {"fecha": date(2025, 8, 2), "hora": time(10, 30), "detalle": "Limpieza dental"},
            {"fecha": date(2025, 8, 3), "hora": time(14, 0), "detalle": "Control post-tratamiento"},
            {"fecha": date(2025, 8, 5), "hora": time(16, 15), "detalle": "Consulta inicial"},
        ]
        
        turnos_creados = 0
        for i, datos in enumerate(turnos_data):
            if i < len(pacientes):
                paciente = pacientes[i]
                estado = estados[0] if estados else None
                
                turno = Turno(
                    paciente_id=paciente.id,
                    fecha=datos["fecha"],
                    hora=datos["hora"],
                    detalle=datos["detalle"],
                    estado=estado.nombre if estado else "Pendiente"
                )
                db.session.add(turno)
                
                # Crear cambio de estado inicial
                if estado:
                    cambio = CambioEstado(
                        turno_id=None,  # Se asignará después del commit
                        estado_id=estado.id,
                        inicio_estado=datetime.now()
                    )
                    db.session.add(turno)
                    db.session.flush()  # Para obtener el ID del turno
                    cambio.turno_id = turno.id
                    db.session.add(cambio)
                
                turnos_creados += 1
                print_step(i+1, f"Turno creado para {paciente.nombre} - {datos['fecha']}")
        
        db.session.commit()
        print_success(f"Total de turnos creados: {turnos_creados}")

def create_sample_operations(app):
    """Crea operaciones de ejemplo"""
    print_header("CREACIÓN DE OPERACIONES DE EJEMPLO")
    
    with app.app_context():
        pacientes = Paciente.query.all()
        codigos = Codigo.query.all()
        
        if not pacientes or not codigos:
            print("⚠️  No hay pacientes o códigos disponibles")
            return
        
        operaciones_data = [
            {"descripcion": "Consulta inicial", "monto": 3000.0, "codigo_idx": 0},
            {"descripcion": "Limpieza dental completa", "monto": 4500.0, "codigo_idx": 1},
            {"descripcion": "Empaste molar superior", "monto": 8000.0, "codigo_idx": 2},
        ]
        
        operaciones_creadas = 0
        for i, datos in enumerate(operaciones_data):
            if i < len(pacientes) and datos["codigo_idx"] < len(codigos):
                paciente = pacientes[i]
                codigo = codigos[datos["codigo_idx"]]
                
                operacion = Operacion(
                    paciente_id=paciente.id,
                    descripcion=datos["descripcion"],
                    monto=datos["monto"],
                    fecha=datetime.now(),
                    codigo_id=codigo.id,
                    observaciones=f"Operación realizada para {paciente.nombre}"
                )
                db.session.add(operacion)
                operaciones_creadas += 1
                print_step(i+1, f"Operación creada: {datos['descripcion']} - ${datos['monto']}")
        
        db.session.commit()
        print_success(f"Total de operaciones creadas: {operaciones_creadas}")

def test_relationships(app):
    """Prueba las relaciones entre modelos"""
    print_header("PRUEBA DE RELACIONES ENTRE MODELOS")
    
    with app.app_context():
        print_step(1, "Probando relación Paciente -> Turnos")
        paciente = Paciente.query.first()
        if paciente:
            turnos = paciente.turnos
            print_success(f"{paciente.nombre} tiene {len(turnos)} turno(s)")
            for turno in turnos:
                print_info(f"   Turno: {turno.fecha} {turno.hora}")
        
        print_step(2, "Probando relación Turno -> Paciente")
        turno = Turno.query.first()
        if turno:
            paciente = turno.paciente
            print_success(f"Turno del {turno.fecha} pertenece a {paciente.nombre}")
        
        print_step(3, "Probando relación Operación -> Código")
        operacion = Operacion.query.first()
        if operacion and operacion.codigo:
            print_success(f"Operación '{operacion.descripcion}' tiene código {operacion.codigo.numero}")
        
        print_step(4, "Probando relación Paciente -> Localidad")
        if paciente and paciente.localidad:
            print_success(f"{paciente.nombre} vive en {paciente.localidad.nombre}")
        
        print_step(5, "Probando relación Paciente -> Obra Social")
        if paciente and paciente.obra_social:
            print_success(f"{paciente.nombre} tiene obra social {paciente.obra_social.nombre}")

def test_backup_system(app):
    """Prueba el sistema de respaldos"""
    print_header("PRUEBA DEL SISTEMA DE RESPALDOS")
    
    with app.app_context():
        print_step(1, "Creando respaldo de la base de datos")
        backup_name = backup_database()
        if backup_name:
            print_success(f"Respaldo creado: {backup_name}")
        
        print_step(2, "Listando respaldos disponibles")
        backups = list_backups()
        print_success(f"Respaldos encontrados: {len(backups)}")
        for backup in backups[:3]:  # Mostrar solo los primeros 3
            print_info(f"   - {backup}")

def generate_summary_report(app):
    """Genera un reporte resumen del sistema"""
    print_header("REPORTE RESUMEN DEL SISTEMA")
    
    with app.app_context():
        # Contar registros en cada tabla
        stats = {
            "Pacientes": Paciente.query.count(),
            "Turnos": Turno.query.count(),
            "Estados": Estado.query.count(),
            "Cambios de Estado": CambioEstado.query.count(),
            "Localidades": Localidad.query.count(),
            "Obras Sociales": ObraSocial.query.count(),
            "Operaciones": Operacion.query.count(),
            "Códigos de Operación": Codigo.query.count(),
        }
        
        print("\n📊 ESTADÍSTICAS DE LA BASE DE DATOS:")
        print("-" * 40)
        total_registros = 0
        for tabla, cantidad in stats.items():
            print(f"   {tabla:<20}: {cantidad:>5} registros")
            total_registros += cantidad
        
        print("-" * 40)
        print(f"   {'TOTAL':<20}: {total_registros:>5} registros")
        
        # Información adicional
        backups = list_backups()
        print(f"\n💾 Respaldos disponibles: {len(backups)}")
        
        print(f"\n🗄️  Base de datos: instance/consultorio.db")
        print(f"📅 Fecha de inicialización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO SISTEMA DE GESTIÓN DE CONSULTORIO ODONTOLÓGICO")
    print("=" * 80)
    
    try:
        # 1. Configuración y base de datos
        app = test_database_config()
        
        # 2. Población de datos maestros
        populate_sample_data(app)
        
        # 3. Creación de datos de ejemplo
        create_sample_patients(app)
        create_sample_appointments(app)
        create_sample_operations(app)
        
        # 4. Pruebas de funcionalidad
        test_relationships(app)
        test_backup_system(app)
        
        # 5. Reporte final
        generate_summary_report(app)
        
        print_header("INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("🎉 El sistema está listo para usar!")
        print("📋 Para ver la base de datos, revisa el archivo: instance/consultorio.db")
        print("💾 Los respaldos se guardan en: instance/backups/")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA INICIALIZACIÓN:")
        print(f"   {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
