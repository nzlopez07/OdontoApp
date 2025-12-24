"""Factories simples para tests."""
from datetime import date, datetime, time
from app.database import db
from app.models import Usuario, Paciente, Turno, Prestacion, Practica, ObraSocial, PrestacionPractica, Gasto
from werkzeug.security import generate_password_hash


def make_usuario(username="admin", rol="ADMIN", password="secret"):
    user = Usuario(
        username=username,
        email=f"{username}@test.local",
        nombre="Test",
        apellido="User",
        rol=rol,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return user


def make_paciente(nombre="Ana", apellido="Perez", dni="12345678", obra_social=None):
    paciente = Paciente(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        telefono="1111-1111",
        direccion="Calle Falsa 123",
        fecha_nac=date(1990, 1, 1),
    )
    if obra_social:
        paciente.obra_social_id = obra_social.id
    db.session.add(paciente)
    db.session.commit()
    return paciente


def make_obra_social(nombre="IPSS"):
    os = ObraSocial(nombre=nombre)
    db.session.add(os)
    db.session.commit()
    return os


def make_practica(codigo="P001", descripcion="Limpieza", monto=1000, proveedor_tipo="Particular", obra_social=None):
    practica = Practica(
        codigo=codigo,
        descripcion=descripcion,
        monto_unitario=monto,
        proveedor_tipo=proveedor_tipo,
        obra_social_id=obra_social.id if obra_social else None,
    )
    db.session.add(practica)
    db.session.commit()
    return practica


def make_turno(paciente, fecha=None, hora=None, estado="Pendiente"):
    turno = Turno(
        paciente_id=paciente.id,
        fecha=fecha or date.today(),
        hora=hora or time(9, 0),
        estado=estado,
    )
    db.session.add(turno)
    db.session.commit()
    return turno


def make_prestacion(paciente, monto=1000, fecha=None, descripcion="Test prestacion"):
    fecha_dt = fecha
    if fecha is None:
        fecha_dt = datetime.combine(date.today(), time(0, 0))
    elif isinstance(fecha, date) and not isinstance(fecha, datetime):
        fecha_dt = datetime.combine(fecha, time(0, 0))

    prestacion = Prestacion(
        paciente_id=paciente.id,
        fecha=fecha_dt,
        monto=monto,
        descripcion=descripcion,
    )
    db.session.add(prestacion)
    db.session.commit()
    return prestacion


def make_prestacion_practica(prestacion, practica, cantidad=1, monto_unitario=None, observaciones=None):
    pp = PrestacionPractica(
        prestacion_id=prestacion.id,
        practica_id=practica.id,
        cantidad=cantidad,
        monto_unitario=monto_unitario,
        observaciones=observaciones,
    )
    db.session.add(pp)
    db.session.commit()
    return pp


def make_gasto(descripcion="Compra insumos", monto=500, fecha=None, categoria="INSUMO", observaciones=None, comprobante=None, creado_por=None):
    gasto = Gasto(
        descripcion=descripcion,
        monto=monto,
        fecha=fecha or date.today(),
        categoria=categoria,
        observaciones=observaciones,
        comprobante=comprobante,
        creado_por_id=creado_por.id if creado_por else None,
    )
    db.session.add(gasto)
    db.session.commit()
    return gasto
