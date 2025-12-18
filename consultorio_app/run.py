#!/usr/bin/env python3
"""
Punto de entrada principal para el Sistema de Gestión de Consultorio Odontológico
Ejecuta el servidor web Flask para la aplicación.
"""

import os
import sys
from app import create_app
from app.database import db
from app.models import *  # Importar todos los modelos para que SQLAlchemy los reconozca
from sqlalchemy import text


def init_default_data():
    """Inicializar datos por defecto en la BD (estados, localidades, obras sociales)."""
    # Estados predefinidos para turnos
    estados_predefinidos = ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']
    for nombre in estados_predefinidos:
        if not Estado.query.filter_by(nombre=nombre).first():
            estado = Estado(nombre=nombre)
            db.session.add(estado)
    
    # Localidades por defecto
    localidades_predefinidas = ['La Plata', 'Tolosa', 'Villa Elisa', 'Gonnet', 'Ringuelet', 'Los Hornos']
    for nombre in localidades_predefinidas:
        if not Localidad.query.filter_by(nombre=nombre).first():
            localidad = Localidad(nombre=nombre)
            db.session.add(localidad)
    
    # Obras sociales por defecto
    obras_sociales_predefinidas = [
        'OSDE', 'Medife', 'Afianzadora Salud', 'Swiss Medical', 
        'Galeno', 'IPAM', 'Farmacia del Dr. Surtidor', 'Particular'
    ]
    for nombre in obras_sociales_predefinidas:
        if not ObraSocial.query.filter_by(nombre=nombre).first():
            obra = ObraSocial(nombre=nombre)
            db.session.add(obra)
    
    db.session.commit()
    print("✅ Datos por defecto inicializados")

def run_migrations_sqlite():
    """Execute DB migrations to align schema with Prestaciones and nro_afiliado.
    SQLite doesn't support renaming FKs directly; perform safe table rebuilds.
    """
    # 1) Rename table 'operaciones' -> 'prestaciones'
    # If prestaciones already exists, skip
    existing_tables = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    table_names = {row[0] for row in existing_tables}

    if 'operaciones' in table_names and 'prestaciones' not in table_names:
        print("🔧 Migrando tabla operaciones -> prestaciones...")
        db.session.execute(text("ALTER TABLE operaciones RENAME TO prestaciones"))
        db.session.commit()

    # 2) Update Turnos: operacion_id -> prestacion_id
    # SQLite requires table rebuild to rename columns
    turnos_cols = db.session.execute(text("PRAGMA table_info('turnos')")).fetchall()
    turnos_col_names = {c[1] for c in turnos_cols}
    if 'operacion_id' in turnos_col_names and 'prestacion_id' not in turnos_col_names:
        print("🔧 Migrando columna turnos.operacion_id -> prestacion_id...")
        db.session.execute(text("BEGIN TRANSACTION"))
        db.session.execute(text(
            "CREATE TABLE IF NOT EXISTS turnos_tmp (\n"
            "    id INTEGER PRIMARY KEY,\n"
            "    paciente_id INTEGER NOT NULL,\n"
            "    fecha DATE NOT NULL,\n"
            "    hora TIME NOT NULL,\n"
            "    detalle STRING,\n"
            "    estado STRING,\n"
            "    prestacion_id INTEGER,\n"
            "    FOREIGN KEY(paciente_id) REFERENCES pacientes(id),\n"
            "    FOREIGN KEY(prestacion_id) REFERENCES prestaciones(id)\n"
            ")"
        ))
        db.session.execute(text(
            "INSERT INTO turnos_tmp (id, paciente_id, fecha, hora, detalle, estado, prestacion_id)\n"
            "SELECT id, paciente_id, fecha, hora, detalle, estado, operacion_id FROM turnos"
        ))
        db.session.execute(text("DROP TABLE turnos"))
        db.session.execute(text("ALTER TABLE turnos_tmp RENAME TO turnos"))
        db.session.execute(text("COMMIT"))
        print("✅ turnos migrados")

    # 3) Update Pacientes: carnet -> nro_afiliado
    pacientes_cols = db.session.execute(text("PRAGMA table_info('pacientes')")).fetchall()
    pacientes_col_names = {c[1] for c in pacientes_cols}
    if 'carnet' in pacientes_col_names and 'nro_afiliado' not in pacientes_col_names:
        print("🔧 Migrando columna pacientes.carnet -> nro_afiliado...")
        db.session.execute(text("BEGIN TRANSACTION"))
        # Build new table with same structure but renamed column
        db.session.execute(text(
            "CREATE TABLE IF NOT EXISTS pacientes_tmp (\n"
            "    id INTEGER PRIMARY KEY,\n"
            "    nombre STRING NOT NULL,\n"
            "    apellido STRING NOT NULL,\n"
            "    dni STRING NOT NULL,\n"
            "    fecha_nac DATE NOT NULL,\n"
            "    telefono STRING,\n"
            "    direccion STRING,\n"
            "    localidad_id INTEGER,\n"
            "    obra_social_id INTEGER,\n"
            "    nro_afiliado STRING,\n"
            "    titular STRING,\n"
            "    parentesco STRING,\n"
            "    lugar_trabajo STRING,\n"
            "    barrio STRING,\n"
            "    FOREIGN KEY(localidad_id) REFERENCES localidades(id),\n"
            "    FOREIGN KEY(obra_social_id) REFERENCES obras_sociales(id)\n"
            ")"
        ))
        db.session.execute(text(
            "INSERT INTO pacientes_tmp (id, nombre, apellido, dni, fecha_nac, telefono, direccion, localidad_id, obra_social_id, nro_afiliado, titular, parentesco, lugar_trabajo, barrio)\n"
            "SELECT id, nombre, apellido, dni, fecha_nac, telefono, direccion, localidad_id, obra_social_id, carnet, titular, parentesco, lugar_trabajo, barrio FROM pacientes"
        ))
        db.session.execute(text("DROP TABLE pacientes"))
        db.session.execute(text("ALTER TABLE pacientes_tmp RENAME TO pacientes"))
        db.session.execute(text("COMMIT"))
        print("✅ pacientes migrados")


def main():
    app = create_app()

    with app.app_context():
        # Verificar si la BD existe y tiene esquema desactualizado
        # Si es desarrollo, recrear tablas desde cero
        if os.environ.get('FLASK_RESET_DB'):
            print("🔄 Eliminando y recreando base de datos...")
            db.drop_all()
        
        db.create_all()
        print("✅ Base de datos verificada")
        
        # Ejecutar migraciones (opt-in)
        if os.environ.get('FLASK_RUN_MIGRATIONS', '').lower() in ('1', 'true', 'yes'):
            run_migrations_sqlite()

        # Inicializar datos por defecto solo si se solicita explícitamente
        seed_flag = os.environ.get('FLASK_SEED_DEFAULTS', '').lower() in ('1', 'true', 'yes')
        if seed_flag:
            init_default_data()
        else:
            print("⏭️  Carga de datos por defecto deshabilitada (FLASK_SEED_DEFAULTS no activo)")
    
    # Configuración del servidor
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Iniciando servidor en http://{host}:{port}")
    print("📋 Para ver ayuda: python help.py")
    print("⚡ Para verificación rápida: python quick_start.py")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()