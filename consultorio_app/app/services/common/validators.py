"""
Validadores comunes reutilizables en los services.

Estos validadores encapsulan reglas de negocio simples y pueden ser
utilizados por múltiples services sin duplicar código.
"""

from datetime import date, time, datetime
from decimal import Decimal
import re


class ValidadorPaciente:
    """Validadores para datos de paciente."""
    
    @staticmethod
    def validar_dni(dni: str) -> tuple:
        """Valida que el DNI sea válido (flexible: 5-10 dígitos para nacionales y extranjeros).
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not dni:
            return False, "El DNI es requerido"
        dni_limpio = dni.strip().replace(".", "").replace("-", "")
        if not dni_limpio.isdigit():
            return False, "El DNI debe contener solo dígitos"
        if len(dni_limpio) < 5 or len(dni_limpio) > 10:
            return False, "El DNI debe tener entre 5 y 10 dígitos (nacionales: 8, extranjeros: 5-9)"
        return True, None
    
    @staticmethod
    def validar_nombre(nombre: str) -> bool:
        """Valida que el nombre no esté vacío."""
        return bool(nombre and nombre.strip())
    
    @staticmethod
    def validar_apellido(apellido: str) -> bool:
        """Valida que el apellido no esté vacío."""
        return bool(apellido and apellido.strip())
    
    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """Valida formato básico de teléfono (opcional, pero si se proporciona, debe ser válido)."""
        if not telefono:
            return True  # teléfono es opcional
        telefono_limpio = telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        return telefono_limpio.isdigit() and len(telefono_limpio) >= 7


class ValidadorTurno:
    """Validadores para datos de turno."""
    
    HORARIO_INICIO = time(8, 0)
    HORARIO_FIN = time(21, 0)
    DURACION_MIN = 5
    DURACION_MAX = 480
    DIAS_LABORABLES = [0, 1, 2, 3, 4, 5]  # Lunes a Sábado
    
    @staticmethod
    def validar_fecha(fecha: date) -> tuple:
        """Valida que la fecha sea válida (no pasada, día laborable).
        
        Returns:
            (es_válida, mensaje_error)
        """
        if fecha < date.today():
            return False, "No se pueden agendar turnos en fechas pasadas"
        
        if fecha.weekday() not in ValidadorTurno.DIAS_LABORABLES:
            return False, "Los turnos solo se pueden agendar de lunes a sábado"
        
        return True, None
    
    @staticmethod
    def validar_hora(hora: time) -> tuple:
        """Valida que la hora esté dentro del horario de atención.
        
        Returns:
            (es_válida, mensaje_error)
        """
        if hora < ValidadorTurno.HORARIO_INICIO or hora >= ValidadorTurno.HORARIO_FIN:
            return False, (
                f"Los turnos solo se pueden agendar entre "
                f"{ValidadorTurno.HORARIO_INICIO.strftime('%H:%M')} y "
                f"{ValidadorTurno.HORARIO_FIN.strftime('%H:%M')}"
            )
        return True, None
    
    @staticmethod
    def validar_duracion(duracion: int) -> tuple:
        """Valida que la duración esté en rango válido.
        
        Returns:
            (es_válida, mensaje_error)
        """
        if duracion < ValidadorTurno.DURACION_MIN or duracion > ValidadorTurno.DURACION_MAX:
            return False, (
                f"La duración debe estar entre {ValidadorTurno.DURACION_MIN} y "
                f"{ValidadorTurno.DURACION_MAX} minutos"
            )
        return True, None


class ValidadorLocalidad:
    """Validadores para datos de localidad."""
    
    @staticmethod
    def normalizar_nombre(nombre: str) -> str:
        """Normaliza el nombre de localidad (comprime espacios, Title Case)."""
        if not nombre:
            return ""
        limpio = ' '.join(nombre.strip().split())
        return limpio.title()
    
    @staticmethod
    def validar_nombre(nombre: str) -> bool:
        """Valida que el nombre no esté vacío."""
        return bool(nombre and nombre.strip())


class ValidadorPrestacion:
    """Validadores para datos de prestación."""
    
    MONTO_MINIMO = Decimal('0.01')
    MONTO_MAXIMO = Decimal('999999.99')
    
    @staticmethod
    def validar_monto(monto: float | Decimal) -> tuple:
        """Valida que el monto sea válido (entre 0.01 y 999999.99).
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not monto:
            return False, "El monto es requerido"
        
        try:
            monto_decimal = Decimal(str(monto))
        except (ValueError, TypeError):
            return False, "El monto debe ser un número válido"
        
        if monto_decimal < ValidadorPrestacion.MONTO_MINIMO:
            return False, f"El monto mínimo es ${ValidadorPrestacion.MONTO_MINIMO}"
        
        if monto_decimal > ValidadorPrestacion.MONTO_MAXIMO:
            return False, f"El monto máximo es ${ValidadorPrestacion.MONTO_MAXIMO}"
        
        return True, None
    
    @staticmethod
    def validar_descuento_porcentaje(descuento: float) -> tuple:
        """Valida que el descuento porcentual esté entre 0 y 100.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if descuento < 0 or descuento > 100:
            return False, "El descuento debe estar entre 0 y 100%"
        return True, None
    
    @staticmethod
    def validar_descuento_fijo(descuento: float) -> tuple:
        """Valida que el descuento fijo sea no negativo.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if descuento < 0:
            return False, "El descuento fijo no puede ser negativo"
        return True, None


class ValidadorGasto:
    """Validadores para datos de gasto."""
    
    CATEGORIAS_VALIDAS = ['MATERIAL', 'INSUMO', 'MATRICULA', 'CURSO', 'OPERATIVO', 'OTRO']
    MONTO_MINIMO = Decimal('0.01')
    MONTO_MAXIMO = Decimal('999999.99')
    
    @staticmethod
    def validar_categoria(categoria: str) -> tuple:
        """Valida que la categoría sea válida.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not categoria or categoria not in ValidadorGasto.CATEGORIAS_VALIDAS:
            return False, f"Categoría inválida. Válidas: {', '.join(ValidadorGasto.CATEGORIAS_VALIDAS)}"
        return True, None
    
    @staticmethod
    def validar_monto(monto: float | Decimal) -> tuple:
        """Valida que el monto sea válido (entre 0.01 y 999999.99).
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not monto:
            return False, "El monto es requerido"
        
        try:
            monto_decimal = Decimal(str(monto))
        except (ValueError, TypeError):
            return False, "El monto debe ser un número válido"
        
        if monto_decimal < ValidadorGasto.MONTO_MINIMO:
            return False, f"El monto mínimo es ${ValidadorGasto.MONTO_MINIMO}"
        
        if monto_decimal > ValidadorGasto.MONTO_MAXIMO:
            return False, f"El monto máximo es ${ValidadorGasto.MONTO_MAXIMO}"
        
        return True, None
    
    @staticmethod
    def validar_descripcion(descripcion: str) -> bool:
        """Valida que la descripción no esté vacía."""
        return bool(descripcion and descripcion.strip() and len(descripcion.strip()) >= 3)


class ValidadorFecha:
    """Validadores para fechas."""
    
    @staticmethod
    def validar_fecha_natalicio(fecha: date) -> tuple:
        """Valida que la fecha de nacimiento sea válida (no futura).
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not fecha:
            return False, "La fecha de nacimiento es requerida"
        
        if fecha > date.today():
            return False, "La fecha de nacimiento no puede ser futura"
        
        return True, None
    
    @staticmethod
    def validar_rango_fechas(fecha_desde: date, fecha_hasta: date) -> tuple:
        """Valida que fecha_desde <= fecha_hasta.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not fecha_desde or not fecha_hasta:
            return False, "Ambas fechas son requeridas"
        
        if fecha_desde > fecha_hasta:
            return False, "La fecha desde no puede ser mayor que la fecha hasta"
        
        return True, None


class ValidadorObraSocial:
    """Validadores para obras sociales."""
    
    @staticmethod
    def validar_nombre(nombre: str) -> tuple:
        """Valida que el nombre de obra social sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not nombre or not nombre.strip():
            return False, "El nombre de obra social es requerido"
        if len(nombre.strip()) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        if len(nombre.strip()) > 100:
            return False, "El nombre no puede exceder 100 caracteres"
        return True, None
    
    @staticmethod
    def validar_codigo(codigo: str) -> tuple:
        """Valida que el código de obra social sea válido (opcional).
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not codigo:  # Es opcional
            return True, None
        if len(codigo.strip()) > 20:
            return False, "El código no puede exceder 20 caracteres"
        return True, None


class ValidadorPractica:
    """Validadores para prácticas odontológicas."""
    
    PROVEEDORES_VALIDOS = ['OSDE', 'IPSS', 'SANCOR', 'PARTICULAR', 'OTRO']
    
    @staticmethod
    def validar_codigo(codigo: str) -> tuple:
        """Valida que el código de práctica sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not codigo or not codigo.strip():
            return False, "El código de práctica es requerido"
        if len(codigo.strip()) > 30:
            return False, "El código no puede exceder 30 caracteres"
        return True, None
    
    @staticmethod
    def validar_descripcion(descripcion: str) -> tuple:
        """Valida que la descripción de práctica sea válida.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not descripcion or not descripcion.strip():
            return False, "La descripción de práctica es requerida"
        if len(descripcion.strip()) < 3:
            return False, "La descripción debe tener al menos 3 caracteres"
        if len(descripcion.strip()) > 200:
            return False, "La descripción no puede exceder 200 caracteres"
        return True, None
    
    @staticmethod
    def validar_proveedor_tipo(proveedor_tipo: str) -> tuple:
        """Valida que el tipo de proveedor sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not proveedor_tipo or proveedor_tipo not in ValidadorPractica.PROVEEDORES_VALIDOS:
            return False, f"Tipo de proveedor inválido. Válidos: {', '.join(ValidadorPractica.PROVEEDORES_VALIDOS)}"
        return True, None
    
    @staticmethod
    def validar_monto_unitario(monto: float | Decimal) -> tuple:
        """Valida que el monto unitario sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if monto is None:
            return False, "El monto unitario es requerido"
        try:
            monto_decimal = Decimal(str(monto))
        except (ValueError, TypeError):
            return False, "El monto debe ser un número válido"
        if monto_decimal < Decimal('0'):
            return False, "El monto unitario no puede ser negativo"
        if monto_decimal > Decimal('999999.99'):
            return False, "El monto unitario no puede exceder $999999.99"
        return True, None


class ValidadorUsuario:
    """Validadores para usuarios."""
    
    ROLES_VALIDOS = ['DUEÑA', 'ODONTOLOGA', 'ADMIN']
    
    @staticmethod
    def validar_username(username: str) -> tuple:
        """Valida que el nombre de usuario sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not username or not username.strip():
            return False, "El nombre de usuario es requerido"
        if len(username.strip()) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"
        if len(username.strip()) > 50:
            return False, "El nombre de usuario no puede exceder 50 caracteres"
        if not username.replace('_', '').replace('-', '').isalnum():
            return False, "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"
        return True, None
    
    @staticmethod
    def validar_password(password: str) -> tuple:
        """Valida que la contraseña sea suficientemente segura.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not password:
            return False, "La contraseña es requerida"
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        if len(password) > 200:
            return False, "La contraseña es demasiado larga"
        return True, None
    
    @staticmethod
    def validar_rol(rol: str) -> tuple:
        """Valida que el rol sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not rol or rol not in ValidadorUsuario.ROLES_VALIDOS:
            return False, f"Rol inválido. Válidos: {', '.join(ValidadorUsuario.ROLES_VALIDOS)}"
        return True, None


class ValidadorCodigo:
    """Validadores para códigos de prácticas."""
    
    @staticmethod
    def validar_numero(numero: str) -> tuple:
        """Valida que el número de código sea válido.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not numero or not numero.strip():
            return False, "El número de código es requerido"
        if len(numero.strip()) > 20:
            return False, "El número no puede exceder 20 caracteres"
        return True, None
    
    @staticmethod
    def validar_descripcion(descripcion: str) -> tuple:
        """Valida que la descripción del código sea válida.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not descripcion or not descripcion.strip():
            return False, "La descripción es requerida"
        if len(descripcion.strip()) < 3:
            return False, "La descripción debe tener al menos 3 caracteres"
        if len(descripcion.strip()) > 200:
            return False, "La descripción no puede exceder 200 caracteres"
        return True, None


class ValidadorOdontograma:
    """Validadores para odontogramas."""
    
    @staticmethod
    def validar_datos_diente(numero_diente: int, estado: str) -> tuple:
        """Valida que los datos de un diente sean válidos.
        
        Returns:
            (es_válido, mensaje_error)
        """
        if not isinstance(numero_diente, int) or numero_diente < 1 or numero_diente > 32:
            return False, "Número de diente debe estar entre 1 y 32"
        
        estados_validos = ['sano', 'cariado', 'obturado', 'endodonciado', 'ausente', 'extraido']
        if estado not in estados_validos:
            return False, f"Estado inválido. Válidos: {', '.join(estados_validos)}"
        
        return True, None
    
    @staticmethod
    def validar_numero_diente(numero: int) -> bool:
        """Valida que el número de diente sea válido (1-32)."""
        return isinstance(numero, int) and 1 <= numero <= 32
