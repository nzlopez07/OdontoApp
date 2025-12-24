# 🔧 Guía de Integración — Validaciones Formales (FASE 3)

**Última Actualización:** Diciembre 2025  
**Estado:** ✅ VALIDADORES Y FORMULARIOS COMPLETADOS | 🟡 INTEGRACIÓN EN RUTAS PENDIENTE

---

## 📋 Resumen Ejecutivo

Se han implementado **validaciones formales** cubriendo **todas las entidades** del sistema con **validación flexibilizada de DNI internacional** (5-10 dígitos).

### ✅ Completado:
- 10 validadores en `app/services/common/validators.py`
- 9 formularios WTF en `app/forms.py`
- Soporte para DNI de 5-10 dígitos (nacionales: 8, extranjeros: flexible)
- Cobertura de 100% de entidades (Paciente, Turno, Prestacion, Gasto, ObraSocial, Practica, Usuario, Codigo, Odontograma, Localidad)

### 🟡 Pendiente:
- Integración de formularios en rutas (pacientes, turnos, prestaciones, gastos, finanzas, login, obras sociales, practicas, codigos)
- Testing end-to-end de validaciones

---

## ✅ Validadores implementados (10 clases, 40+ métodos)

### 1. ValidadorPaciente
```python
def validar_dni(dni: str) -> tuple  # (is_valid, mensaje)
def validar_nombre(nombre: str) -> tuple
def validar_apellido(apellido: str) -> tuple
def validar_telefono(telefono: str) -> tuple
```
**DNI Flexible:** Acepta 5-10 dígitos (nacionales 8, extranjeros 5-9)

### 2. ValidadorTurno
```python
def validar_fecha(fecha: date) -> tuple
def validar_hora(hora: time) -> tuple
def validar_duracion(duracion: int) -> tuple
```
**Reglas:** Fecha no pasada, lunes-sábado. Hora 08:00-21:00. Duración 5-480 minutos.

### 3. ValidadorPrestacion
```python
def validar_monto(monto: float) -> tuple
def validar_descuento_porcentaje(porcentaje: float) -> tuple
def validar_descuento_fijo(monto_fijo: float) -> tuple
```
**Reglas:** Monto $0.01-$999,999.99. Descuentos 0-100%.

### 4. ValidadorGasto
```python
def validar_categoria(categoria: str) -> tuple
def validar_monto(monto: float) -> tuple
def validar_descripcion(descripcion: str) -> tuple
```
**Categorías válidas:** MATERIAL, INSUMO, MATRICULA, CURSO, OPERATIVO, OTRO.

### 5. ValidadorFecha
```python
def validar_fecha_natalicio(fecha: date) -> tuple
def validar_rango_fechas(fecha_desde: date, fecha_hasta: date) -> tuple
```
**Reglas:** Natalicio no futuro. Rango: desde <= hasta.

### 6. ValidadorObraSocial ⭐ NUEVO
```python
def validar_nombre(nombre: str) -> tuple
def validar_codigo(codigo: str) -> tuple
```
**Reglas:** Nombre 2-100 chars. Código máx 20 chars (opcional).

### 7. ValidadorPractica ⭐ NUEVO
```python
def validar_codigo(codigo: str) -> tuple
def validar_descripcion(descripcion: str) -> tuple
def validar_proveedor_tipo(tipo: str) -> tuple
def validar_monto_unitario(monto: float) -> tuple
```
**Tipos de Proveedor:** OSDE, IPSS, SANCOR, PARTICULAR, OTRO.

### 8. ValidadorUsuario ⭐ NUEVO
```python
def validar_username(username: str) -> tuple
def validar_password(password: str) -> tuple
def validar_rol(rol: str) -> tuple
```
**Roles válidos:** DUEÑA, ODONTOLOGA, ADMIN.

### 9. ValidadorCodigo ⭐ NUEVO
```python
def validar_numero(numero: str) -> tuple
def validar_descripcion(descripcion: str) -> tuple
```

### 10. ValidadorOdontograma ⭐ NUEVO
```python
def validar_datos_diente(datos: dict) -> tuple
def validar_numero_diente(numero: int) -> tuple
```

---

## 📝 Formularios WTF implementados (9 formularios)

Todos los formularios:
- ✅ Integran validadores custom
- ✅ Incluyen protección CSRF automática
- ✅ Soportan dynamic select fields (localidades, obras sociales, etc.)
- ✅ Generan mensajes de error en español

### Formularios Listados:
1. **PacienteForm** - nombre, apellido, dni, fecha_nac, telefono, etc.
2. **TurnoForm** - paciente_id, fecha, hora, duracion, estado
3. **PrestacionForm** - paciente_id, descripcion, monto, descuentos
4. **GastoForm** - descripcion, monto, fecha, categoria
5. **LoginForm** - username, password
6. **ObraSocialForm** - nombre, codigo
7. **PracticaForm** - codigo, descripcion, proveedor_tipo, monto_unitario
8. **RegistroUsuarioForm** - username, password, password_confirm, rol
9. **CodigoForm** - numero, descripcion

---

## 🛠️ Cómo integrar validaciones en las rutas

### Paso 1: Importar formulario en la ruta

```python
from app.forms import (
    PacienteForm, TurnoForm, PrestacionForm, GastoForm,
    ObraSocialForm, PracticaForm, RegistroUsuarioForm, CodigoForm, LoginForm
)
```

### Paso 2: Instanciar y procesar en GET/POST

**Antes (sin validación formal):**
```python
@main_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
def crear_paciente():
    if request.method == 'POST':
        # Validación manual, dispersa
        if not request.form.get('nombre'):
            flash('El nombre es requerido', 'error')
            return redirect(url_for('main.crear_paciente'))
        # ... más validaciones manuales
```

**Después (con WTF):**
```python
from app.forms import PacienteForm
from app.models import Localidad, ObraSocial
from app.services.paciente import CrearPacienteService

@main_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
def crear_paciente():
    form = PacienteForm()
    
    # Poblar select fields (localidades, obras sociales)
    form.localidad_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(loc.id, loc.nombre) for loc in Localidad.query.order_by(Localidad.nombre).all()]
    ]
    form.obra_social_id.choices = [
        (0, '--- Seleccionar ---'),
        *[(os.id, os.nombre) for os in ObraSocial.query.order_by(ObraSocial.nombre).all()]
    ]
    
    if form.validate_on_submit():
        try:
            # Los datos ya están validados por WTF
            paciente = CrearPacienteService.crear(
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                dni=form.dni.data,
                fecha_nac=form.fecha_nac.data,
                telefono=form.telefono.data or None,
                direccion=form.direccion.data or None,
                localidad_id=form.localidad_id.data or None,
                obra_social_id=form.obra_social_id.data or None,
                nro_afiliado=form.nro_afiliado.data or None,
            )
            flash(f'Paciente "{paciente.apellido}, {paciente.nombre}" creado', 'success')
            return redirect(url_for('main.detalle_paciente', paciente_id=paciente.id))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('pacientes/nuevo.html', form=form)
```

### Paso 3: Actualizar plantilla para usar form

**Antes (sin WTF):**
```html
<form method="POST">
    <input type="text" name="nombre" placeholder="Nombre" required>
    <input type="text" name="apellido" placeholder="Apellido" required>
    <button type="submit">Guardar</button>
</form>
```

**Después (con WTF):**
```html
<form method="POST" novalidate>
    {{ form.hidden_tag() }}
    
    <div class="form-group">
        {{ form.nombre.label }}
        {{ form.nombre(class="form-control" + (" is-invalid" if form.nombre.errors else "")) }}
        {% if form.nombre.errors %}
        <div class="invalid-feedback">
            {% for error in form.nombre.errors %}
            <div>{{ error }}</div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    
    <div class="form-group">
        {{ form.apellido.label }}
        {{ form.apellido(class="form-control" + (" is-invalid" if form.apellido.errors else "")) }}
        {% if form.apellido.errors %}
        <div class="invalid-feedback">
            {% for error in form.apellido.errors %}
            <div>{{ error }}</div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    
    {{ form.submit(class="btn btn-primary") }}
</form>
```

---

## 📋 Checklist de integración por ruta

### Pacientes
- [ ] `/pacientes/nuevo` - Integrar PacienteForm
- [ ] `/pacientes/<id>/editar` - Integrar PacienteForm (pre-poblar campos)

### Turnos
- [ ] `/turnos/nuevo` - Integrar TurnoForm
- [ ] `/turnos/<id>/editar` - Integrar TurnoForm (pre-poblar campos)

### Prestaciones
- [ ] `/prestaciones/nueva` - Integrar PrestacionForm
- [ ] `/prestaciones/<id>/editar` - Integrar PrestacionForm

### Finanzas/Gastos
- [ ] `/finanzas/gastos/nuevo` - Integrar GastoForm
- [ ] `/finanzas/gastos/<id>/editar` - Integrar GastoForm

### Obras Sociales
- [ ] `/obras-sociales/nueva` - Integrar ObraSocialForm
- [ ] `/obras-sociales/<id>/editar` - Integrar ObraSocialForm

### Prácticas
- [ ] `/practicas/nueva` - Integrar PracticaForm
- [ ] `/practicas/<id>/editar` - Integrar PracticaForm

### Códigos
- [ ] `/codigos/nuevo` - Integrar CodigoForm
- [ ] `/codigos/<id>/editar` - Integrar CodigoForm

### Usuarios
- [ ] `/admin/usuarios/nuevo` - Integrar RegistroUsuarioForm
- [ ] `/login` - Integrar LoginForm

---

## 🎯 Características especiales

### DNI Flexible (Internacional)

La validación DNI ahora **acepta 5-10 dígitos**:

```python
# Ejemplos válidos:
ValidadorPaciente.validar_dni("12345678")      # ✅ Nacional (8 dígitos)
ValidadorPaciente.validar_dni("12345")         # ✅ Extranjero (5 dígitos)
ValidadorPaciente.validar_dni("1234567890")    # ✅ Extranjero (10 dígitos)
ValidadorPaciente.validar_dni("1234")          # ❌ Muy corto (< 5)
ValidadorPaciente.validar_dni("12345678901")   # ❌ Muy largo (> 10)
```

Retorna: `(is_valid: bool, mensaje: str)`

### Validadores Turnos Superpuestos (Opcional)

Para evitar que dos turnos se creen al mismo tiempo para el mismo paciente:

```python
# En ValidadorTurno
@staticmethod
def validar_turno_superpuesto(paciente_id: int, fecha: date, hora: time, turno_id: int = None) -> tuple:
    """Valida que no haya otro turno en el mismo horario."""
    from app.models import Turno
    
    query = Turno.query.filter(
        Turno.paciente_id == paciente_id,
        Turno.fecha == fecha,
        Turno.hora == hora,
        Turno.estado != 'Cancelado'
    )
    
    # Excluir el turno siendo editado
    if turno_id:
        query = query.filter(Turno.id != turno_id)
    
    turno_existente = query.first()
    
    if turno_existente:
        return False, "Ya existe un turno para este paciente en ese horario"
    
    return True, None
```

---

## 🔐 Seguridad CSRF

Flask-WTF incluye protección CSRF automática. Asegúrate de:

1. ✅ Usar `{{ form.hidden_tag() }}` en todas las plantillas
2. ✅ El `SECRET_KEY` está configurado en `app/__init__.py`
3. ✅ No deshabilitar CSRF protection a menos que sea necesario

---

## 📝 Cómo agregar validadores custom

Si necesitas agregar un validador custom a un campo:

```python
from wtforms.validators import ValidationError

class MiForm(FlaskForm):
    campo = StringField('Campo')
    
    def validate_campo(self, field):
        # Se ejecuta automáticamente después de otros validadores
        if 'palabra_prohibida' in field.data.lower():
            raise ValidationError('Esta palabra no está permitida')
```

---

## 🧪 Testing

Una vez integrado, prueba:

1. **Form vacío** → Debe mostrar errores
2. **DNI con 7 dígitos** → Debe aceptar (extranjero)
3. **DNI con 4 dígitos** → Debe rechazar
4. **Fecha futura** → Debe rechazar
5. **Monto negativo** → Debe rechazar
6. **Datos válidos** → Debe guardar

### Script de prueba manual:

```python
# En la terminal Flask
from app.services.common.validators import ValidadorPaciente

# Test DNI flexible
print(ValidadorPaciente.validar_dni("12345678"))      # (True, None) - Nacional
print(ValidadorPaciente.validar_dni("12345"))         # (True, None) - Extranjero
print(ValidadorPaciente.validar_dni("1234"))          # (False, "...")
```

---

## 📚 Documentación oficial

- [Flask-WTF](https://flask-wtf.readthedocs.io/)
- [WTForms Validators](https://wtforms.readthedocs.io/en/stable/validators/)
- [Flask-WTF Custom Validators](https://flask-wtf.readthedocs.io/en/stable/)

---

## 🚀 Próximos pasos

**Prioridad 1 (Crítico):**
- [ ] Integrar PacienteForm en `/pacientes/nuevo` y `/pacientes/<id>/editar`
- [ ] Integrar TurnoForm en `/turnos/nuevo` y `/turnos/<id>/editar`
- [ ] Integrar LoginForm en `/login`

**Prioridad 2 (Alto):**
- [ ] Integrar PrestacionForm
- [ ] Integrar GastoForm
- [ ] Integrar ObraSocialForm

**Prioridad 3 (Medio):**
- [ ] Integrar PracticaForm
- [ ] Integrar CodigoForm
- [ ] Integrar RegistroUsuarioForm

**Prioridad 4 (Futuro):**
- [ ] Validación de turnos superpuestos
- [ ] Validación de duplicados (DNI, username)
- [ ] Validación más sofisticada de contraseñas

---

**Estado Final FASE 3:** ✅ Validadores y formularios completados. 🟡 Integración en rutas pendiente.

Sigue la [Guía de Arquitectura](decisiones_tecnicas.md) para mantener coherencia en la integración.
