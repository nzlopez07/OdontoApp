"""
Formularios de validación usando Flask-WTF.

Centraliza la validación de entrada para todos los formularios principales.
Integra validadores custom con WTF para una experiencia consistente.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, TelField,
    DateField, TimeField, IntegerField, DecimalField,
    SelectField, TextAreaField, SubmitField, HiddenField, BooleanField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, Optional,
    ValidationError, NumberRange
)
from datetime import date
from decimal import Decimal

from app.services.common.validators import (
    ValidadorPaciente,
    ValidadorTurno,
    ValidadorPrestacion,
    ValidadorGasto,
    ValidadorFecha,
    ValidadorObraSocial,
    ValidadorPractica,
    ValidadorUsuario,
    ValidadorCodigo,
    ValidadorOdontograma,
)


class PacienteForm(FlaskForm):
    """Formulario para crear/editar pacientes."""
    
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
        ]
    )
    
    apellido = StringField(
        'Apellido',
        validators=[
            DataRequired(message='El apellido es requerido'),
            Length(min=2, max=100, message='El apellido debe tener entre 2 y 100 caracteres')
        ]
    )
    
    dni = StringField(
        'DNI',
        validators=[DataRequired(message='El DNI es requerido')]
    )
    
    fecha_nac = DateField(
        'Fecha de Nacimiento',
        validators=[DataRequired(message='La fecha de nacimiento es requerida')]
    )
    
    telefono = TelField(
        'Teléfono',
        validators=[Optional()]
    )
    
    lugar_trabajo = StringField(
        'Lugar de Trabajo',
        validators=[Optional(), Length(max=200)]
    )
    
    direccion = StringField(
        'Dirección',
        validators=[Optional(), Length(max=200)]
    )
    
    barrio = StringField(
        'Barrio',
        validators=[Optional(), Length(max=100)]
    )
    
    localidad_id = SelectField(
        'Localidad',
        coerce=int,
        validators=[Optional()]
    )
    
    obra_social_id = SelectField(
        'Obra Social',
        coerce=int,
        validators=[Optional()]
    )
    
    nro_afiliado = StringField(
        'Nro. Afiliado',
        validators=[Optional(), Length(max=50)]
    )
    
    titular = StringField(
        'Titular',
        validators=[Optional(), Length(max=100)]
    )
    
    parentesco = StringField(
        'Parentesco',
        validators=[Optional(), Length(max=50)]
    )
    
    submit = SubmitField('Guardar Paciente')
    
    def validate_dni(self, field):
        """Validador custom para DNI."""
        es_válido, mensaje = ValidadorPaciente.validar_dni(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
    
    def validate_fecha_nac(self, field):
        """Validador custom para fecha de nacimiento."""
        if field.data:
            es_válida, mensaje = ValidadorFecha.validar_fecha_natalicio(field.data)
            if not es_válida:
                raise ValidationError(mensaje)


class TurnoForm(FlaskForm):
    """Formulario para crear/editar turnos."""
    
    paciente_id = SelectField(
        'Paciente',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un paciente')]
    )
    
    fecha = DateField(
        'Fecha',
        validators=[DataRequired(message='La fecha es requerida')]
    )
    
    hora = TimeField(
        'Hora',
        validators=[DataRequired(message='La hora es requerida')]
    )
    
    duracion_horas = IntegerField(
        'Horas',
        default=0,
        validators=[
            DataRequired(message='Las horas son requeridas'),
            NumberRange(min=0, max=8, message='Las horas deben estar entre 0 y 8')
        ]
    )
    
    duracion_minutos = IntegerField(
        'Minutos',
        default=30,
        validators=[
            DataRequired(message='Los minutos son requeridos'),
            NumberRange(min=0, max=59, message='Los minutos deben estar entre 0 y 59')
        ]
    )
    
    detalle = TextAreaField(
        'Detalle',
        validators=[Optional(), Length(max=500)]
    )
    
    estado = SelectField(
        'Estado',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Confirmado', 'Confirmado'),
            ('Atendido', 'Atendido'),
            ('NoAtendido', 'No Atendido'),
            ('Cancelado', 'Cancelado')
        ],
        validators=[DataRequired(message='Debe seleccionar un estado')]
    )
    
    submit = SubmitField('Guardar Turno')
    
    def validate_fecha(self, field):
        """Validador custom para fecha."""
        if field.data:
            es_válida, mensaje = ValidadorTurno.validar_fecha(field.data)
            if not es_válida:
                raise ValidationError(mensaje)
    
    def validate_hora(self, field):
        """Validador custom para hora."""
        if field.data:
            es_válida, mensaje = ValidadorTurno.validar_hora(field.data)
            if not es_válida:
                raise ValidationError(mensaje)


class PrestacionForm(FlaskForm):
    """Formulario para crear/editar prestaciones."""
    
    paciente_id = SelectField(
        'Paciente',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un paciente')]
    )
    
    descripcion = StringField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es requerida'),
            Length(min=3, max=200)
        ]
    )
    
    monto = HiddenField(
        'Monto',
        validators=[Optional()]
    )
    
    descuento_porcentaje = StringField(
        'Descuento (%)',
        validators=[Optional()]
    )
    
    descuento_fijo = StringField(
        'Descuento Fijo ($)',
        validators=[Optional()]
    )
    
    observaciones = TextAreaField(
        'Observaciones',
        validators=[Optional(), Length(max=500)]
    )
    
    submit = SubmitField('Guardar Prestación')
    
    def validate_descuento_porcentaje(self, field):
        """Validador custom para descuento porcentaje."""
        # Solo validar si el campo tiene un valor no vacío
        if field.data:
            valor_str = str(field.data).strip()
            if valor_str and valor_str not in ['0', '0.0', '0.00']:  # Si tiene contenido y no es solo "0"
                # Validar que no tenga caracteres inválidos
                if '-' in valor_str or not valor_str.replace('.', '', 1).replace(',', '', 1).isdigit():
                    raise ValidationError('Ingrese un valor numérico válido (solo números positivos)')
                try:
                    valor = float(valor_str.replace(',', '.'))
                    if valor < 0:
                        raise ValidationError('El descuento no puede ser negativo')
                    if valor > 100:
                        raise ValidationError('El descuento no puede ser mayor a 100')
                except ValueError:
                    raise ValidationError('Ingrese un valor numérico válido')
    
    def validate_descuento_fijo(self, field):
        """Validador custom para descuento fijo."""
        # Solo validar si el campo tiene un valor no vacío
        if field.data:
            valor_str = str(field.data).strip()
            if valor_str and valor_str not in ['0', '0.0', '0.00']:  # Si tiene contenido y no es solo "0"
                # Validar que no tenga caracteres inválidos
                if '-' in valor_str or not valor_str.replace('.', '', 1).replace(',', '', 1).isdigit():
                    raise ValidationError('Ingrese un valor numérico válido (solo números positivos)')
                try:
                    valor = float(valor_str.replace(',', '.'))
                    if valor < 0:
                        raise ValidationError('El descuento fijo no puede ser negativo')
                except ValueError:
                    raise ValidationError('Ingrese un valor numérico válido')


class GastoForm(FlaskForm):
    """Formulario para crear/editar gastos."""
    
    descripcion = StringField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es requerida'),
            Length(min=3, max=200)
        ]
    )
    
    monto = DecimalField(
        'Monto ($)',
        places=2,
        validators=[
            DataRequired(message='El monto es requerido'),
            NumberRange(min=0.01, message='El monto debe ser mayor a $0.01')
        ]
    )
    
    fecha = DateField(
        'Fecha',
        validators=[DataRequired(message='La fecha es requerida')]
    )
    
    categoria = SelectField(
        'Categoría',
        choices=[
            ('MATERIAL', 'Material'),
            ('INSUMO', 'Insumo'),
            ('MATRICULA', 'Matrícula'),
            ('CURSO', 'Curso'),
            ('OPERATIVO', 'Operativo'),
            ('OTRO', 'Otro')
        ],
        validators=[DataRequired(message='Debe seleccionar una categoría')]
    )
    
    observaciones = TextAreaField(
        'Observaciones',
        validators=[Optional(), Length(max=500)]
    )
    
    submit = SubmitField('Guardar Gasto')
    
    def validate_monto(self, field):
        """Validador custom para monto."""
        if field.data:
            es_válido, mensaje = ValidadorGasto.validar_monto(field.data)
            if not es_válido:
                raise ValidationError(mensaje)


class LoginForm(FlaskForm):
    """Formulario de login."""
    
    username = StringField(
        'Usuario',
        validators=[
            DataRequired(message='El usuario es requerido'),
            Length(min=3, max=50)
        ]
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message='La contraseña es requerida')]
    )
    
    remember = BooleanField('Recordarme')
    
    submit = SubmitField('Iniciar Sesión')


class ObraSocialForm(FlaskForm):
    """Formulario para crear/editar obras sociales."""
    
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=2, max=100)
        ]
    )
    
    codigo = StringField(
        'Código',
        validators=[Optional(), Length(max=20)]
    )
    
    submit = SubmitField('Guardar Obra Social')
    
    def validate_nombre(self, field):
        """Validador custom para nombre."""
        es_válido, mensaje = ValidadorObraSocial.validar_nombre(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
    
    def validate_codigo(self, field):
        """Validador custom para código."""
        es_válido, mensaje = ValidadorObraSocial.validar_codigo(field.data)
        if not es_válido:
            raise ValidationError(mensaje)


class PracticaForm(FlaskForm):
    """Formulario para crear/editar prácticas."""
    
    codigo = StringField(
        'Código',
        validators=[
            DataRequired(message='El código es requerido'),
            Length(max=30)
        ]
    )
    
    descripcion = StringField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es requerida'),
            Length(min=3, max=200)
        ]
    )
    
    obra_social_id = SelectField(
        'Obra Social',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una obra social')]
    )
    
    monto_unitario = DecimalField(
        'Monto Unitario ($)',
        places=2,
        validators=[
            DataRequired(message='El monto unitario es requerido'),
            NumberRange(min=0, message='El monto no puede ser negativo')
        ]
    )
    
    submit = SubmitField('Guardar Práctica')
    
    def validate_codigo(self, field):
        """Validador custom para código."""
        es_válido, mensaje = ValidadorPractica.validar_codigo(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
    
    def validate_descripcion(self, field):
        """Validador custom para descripción."""
        es_válido, mensaje = ValidadorPractica.validar_descripcion(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
    
    def validate_monto_unitario(self, field):
        """Validador custom para monto."""
        es_válido, mensaje = ValidadorPractica.validar_monto_unitario(field.data)
        if not es_válido:
            raise ValidationError(mensaje)


class RegistroUsuarioForm(FlaskForm):
    """Formulario para registrar nuevos usuarios."""
    
    username = StringField(
        'Nombre de Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es requerido'),
            Length(min=3, max=50)
        ]
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida'),
            Length(min=6, max=200)
        ]
    )
    
    password_confirm = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Debe confirmar la contraseña'),
            EqualTo('password', message='Las contraseñas no coinciden')
        ]
    )
    
    rol = SelectField(
        'Rol',
        choices=[
            ('DUEÑA', 'Dueña'),
            ('ODONTOLOGA', 'Odontóloga'),
            ('ADMIN', 'Administrador')
        ],
        validators=[DataRequired(message='Debe seleccionar un rol')]
    )
    
    submit = SubmitField('Registrar Usuario')
    
    def validate_username(self, field):
        """Validador custom para username."""
        es_válido, mensaje = ValidadorUsuario.validar_username(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
    
    def validate_password(self, field):
        """Validador custom para password."""
        es_válido, mensaje = ValidadorUsuario.validar_password(field.data)
        if not es_válido:
            raise ValidationError(mensaje)


class CodigoForm(FlaskForm):
    """Formulario para crear/editar códigos de prácticas."""
    
    numero = StringField(
        'Número',
        validators=[
            DataRequired(message='El número es requerido'),
            Length(max=20)
        ]
    )
    
    descripcion = StringField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es requerida'),
            Length(min=3, max=200)
        ]
    )
    
    submit = SubmitField('Guardar Código')
    
    def validate_numero(self, field):
        """Validador custom para número."""
        es_válido, mensaje = ValidadorCodigo.validar_numero(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
    
    def validate_descripcion(self, field):
        """Validador custom para descripción."""
        es_válido, mensaje = ValidadorCodigo.validar_descripcion(field.data)
        if not es_válido:
            raise ValidationError(mensaje)
