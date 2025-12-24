# 🎯 QUICK REFERENCE — FASE 3 Validaciones

## ⚡ Quick Import

```python
# En rutas:
from app.forms import PacienteForm, TurnoForm, PrestacionForm, GastoForm

# En services (si necesitas validadores sin formulario):
from app.services.common.validators import ValidadorPaciente, ValidadorTurno
```

---

## ⚡ Quick Pattern: Integración en una Ruta

```python
from flask import render_template, redirect, url_for, flash
from app.forms import PacienteForm
from app.models import Localidad, ObraSocial

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
def crear_paciente():
    form = PacienteForm()
    
    # Población de selects (IMPORTANTE - hacerlo DESPUÉS de instanciar)
    if request.method == 'GET' or True:  # Siempre al entrar
        form.localidad_id.choices = [(0, '---')] + \
            [(l.id, l.nombre) for l in Localidad.query.all()]
        form.obra_social_id.choices = [(0, '---')] + \
            [(o.id, o.nombre) for o in ObraSocial.query.all()]
    
    if form.validate_on_submit():
        # ✅ Los datos YA están validados
        paciente = CrearPacienteService.crear(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            dni=form.dni.data,
            # ... resto de campos
        )
        flash(f'Paciente "{paciente.nombre}" creado', 'success')
        return redirect(url_for('detalle_paciente', id=paciente.id))
    
    return render_template('pacientes/nuevo.html', form=form)
```

---

## ⚡ Quick Pattern: Plantilla

```html
<form method="POST" novalidate>
    {{ form.hidden_tag() }}  <!-- ⚠️ REQUERIDO para CSRF -->
    
    {% macro render_field(field) %}
        <div class="form-group">
            {{ field.label }}
            {{ field(class="form-control" + (" is-invalid" if field.errors else "")) }}
            {% if field.errors %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            {% endif %}
        </div>
    {% endmacro %}
    
    {{ render_field(form.nombre) }}
    {{ render_field(form.apellido) }}
    {{ render_field(form.dni) }}
    
    <button type="submit" class="btn btn-primary">Guardar</button>
</form>
```

---

## ⚡ Quick Reference: Validadores Disponibles

| Validador | Método | Acepta |
|-----------|--------|--------|
| ValidadorPaciente | validar_dni() | 5-10 dígitos |
| ValidadorTurno | validar_fecha() | Fecha no pasada, lun-sab |
| ValidadorPrestacion | validar_monto() | $0.01-$999,999.99 |
| ValidadorGasto | validar_categoria() | MATERIAL, INSUMO, etc. |
| ValidadorFecha | validar_fecha_natalicio() | Fecha no futura |
| ValidadorObraSocial | validar_nombre() | 2-100 caracteres |
| ValidadorPractica | validar_proveedor_tipo() | OSDE, IPSS, etc. |
| ValidadorUsuario | validar_rol() | DUEÑA, ODONTOLOGA, ADMIN |
| ValidadorCodigo | validar_numero() | Máx 20 caracteres |
| ValidadorOdontograma | validar_numero_diente() | 1-32 |

---

## ⚡ Quick Reference: Formularios Disponibles

```python
from app.forms import (
    PacienteForm,           # (nombre, apellido, dni, fecha_nac, telefono)
    TurnoForm,              # (paciente_id, fecha, hora, duracion, estado)
    PrestacionForm,         # (paciente_id, descripcion, monto, descuentos)
    GastoForm,              # (descripcion, monto, fecha, categoria)
    LoginForm,              # (username, password)
    ObraSocialForm,         # (nombre, codigo)
    PracticaForm,           # (codigo, descripcion, proveedor_tipo, monto)
    RegistroUsuarioForm,    # (username, password, password_confirm, rol)
    CodigoForm,             # (numero, descripcion)
)
```

---

## ⚡ Quick Reference: Rutas para Integrar

**CRÍTICAS (hazlo primero):**
- [ ] `GET/POST /pacientes/nuevo` → PacienteForm
- [ ] `GET/POST /turnos/nuevo` → TurnoForm
- [ ] `GET/POST /login` → LoginForm

**DESPUÉS:**
- [ ] `/pacientes/<id>/editar` → PacienteForm
- [ ] `/turnos/<id>/editar` → TurnoForm
- [ ] `/prestaciones/nueva` → PrestacionForm
- [ ] `/finanzas/gastos/nuevo` → GastoForm
- Y 11 rutas más...

---

## ⚡ Quick Validation: DNI Test

```python
from app.services.common.validators import ValidadorPaciente

# Estos son VÁLIDOS:
ValidadorPaciente.validar_dni("12345678")      # Nacional ✅
ValidadorPaciente.validar_dni("12345")         # Extranjero ✅
ValidadorPaciente.validar_dni("1234567890")    # Extranjero ✅

# Estos son INVÁLIDOS:
ValidadorPaciente.validar_dni("1234")          # Muy corto ❌
ValidadorPaciente.validar_dni("12345678901")   # Muy largo ❌
```

---

## ⚡ Common Errors & Fixes

### Error: "form.localidad_id.choices is not set"
**Solución:** Poblar las opciones DESPUÉS de instanciar el formulario
```python
form = PacienteForm()  # Primero instanciar
form.localidad_id.choices = [...]  # LUEGO poblar
```

### Error: "CSRF token missing"
**Solución:** Incluir `{{ form.hidden_tag() }}` en la plantilla
```html
<form method="POST" novalidate>
    {{ form.hidden_tag() }}  <!-- ⚠️ ESTO ES OBLIGATORIO -->
    ...
</form>
```

### Error: "This field is required"
**Solución:** Los campos tienen validadores automáticos. Pasar datos válidos:
```python
if form.validate_on_submit():
    # ✅ Los datos ya están limpios y validados
    service.crear(**form.data)
```

### Error: "Invalid DNI"
**Solución:** Aceptar 5-10 dígitos (no solo 8)
```python
# Estos ahora son VÁLIDOS:
"12345"         # ✅ Extranjero, 5 dígitos
"12345678"      # ✅ Nacional, 8 dígitos
"1234567890"    # ✅ Extranjero, 10 dígitos
```

---

## ⚡ Testing Rápido

```bash
# En consola Python
python
>>> from app.services.common.validators import ValidadorPaciente
>>> ValidadorPaciente.validar_dni("12345678")
(True, None)
>>> ValidadorPaciente.validar_dni("123")
(False, 'El DNI debe tener entre 5 y 10 dígitos...')
```

---

## 📚 Documentación Completa

- **[FASE3_VALIDACIONES.md](FASE3_VALIDACIONES.md)** — Guía completa
- **[FASE3_RESUMEN.md](FASE3_RESUMEN.md)** — Resumen ejecutivo
- **[FASE3_CHECKLIST.md](FASE3_CHECKLIST.md)** — Checklist de tareas

---

**Próximo paso:** Integrar PacienteForm en `/pacientes/nuevo` 🚀
