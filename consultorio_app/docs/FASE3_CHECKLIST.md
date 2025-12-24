# 📋 CHECKLIST FASE 3 - VALIDACIONES FORMALES

**Última Actualización:** Diciembre 2025  
**Responsable:** GitHub Copilot  
**Estado Actual:** ✅ COMPLETADO (Validadores + Formularios) | 🟡 PENDIENTE (Integración en Rutas)

---

## ✅ TAREA 1: Implementar Validadores (COMPLETADO)

### Validadores Core
- [x] ValidadorPaciente (4 métodos)
  - [x] validar_dni() - Flexible 5-10 dígitos
  - [x] validar_nombre()
  - [x] validar_apellido()
  - [x] validar_telefono()

- [x] ValidadorTurno (3 métodos)
  - [x] validar_fecha()
  - [x] validar_hora()
  - [x] validar_duracion()

- [x] ValidadorPrestacion (3 métodos)
  - [x] validar_monto()
  - [x] validar_descuento_porcentaje()
  - [x] validar_descuento_fijo()

- [x] ValidadorGasto (3 métodos)
  - [x] validar_categoria()
  - [x] validar_monto()
  - [x] validar_descripcion()

- [x] ValidadorFecha (2 métodos)
  - [x] validar_fecha_natalicio()
  - [x] validar_rango_fechas()

### Validadores Extensión (NUEVOS)
- [x] ValidadorObraSocial (2 métodos)
  - [x] validar_nombre()
  - [x] validar_codigo()

- [x] ValidadorPractica (4 métodos)
  - [x] validar_codigo()
  - [x] validar_descripcion()
  - [x] validar_proveedor_tipo()
  - [x] validar_monto_unitario()

- [x] ValidadorUsuario (3 métodos)
  - [x] validar_username()
  - [x] validar_password()
  - [x] validar_rol()

- [x] ValidadorCodigo (2 métodos)
  - [x] validar_numero()
  - [x] validar_descripcion()

- [x] ValidadorOdontograma (2 métodos)
  - [x] validar_datos_diente()
  - [x] validar_numero_diente()

### Validadores Pre-existentes
- [x] ValidadorLocalidad (pre-existente)

**Archivos:**
- [x] `app/services/common/validators.py` - ✅ 11 clases, 40+ métodos

---

## ✅ TAREA 2: Crear Formularios WTF (COMPLETADO)

### Formularios Implementados
- [x] PacienteForm
  - [x] nombre, apellido, dni (con validador custom)
  - [x] fecha_nac, telefono, direccion
  - [x] localidad_id, obra_social_id, nro_afiliado

- [x] TurnoForm
  - [x] paciente_id, fecha, hora
  - [x] duracion, detalle, estado

- [x] PrestacionForm
  - [x] paciente_id, descripcion, monto
  - [x] descuento_porcentaje, descuento_fijo, observaciones

- [x] GastoForm
  - [x] descripcion, monto, fecha
  - [x] categoria, observaciones

- [x] LoginForm
  - [x] username, password

- [x] ObraSocialForm
  - [x] nombre, codigo

- [x] PracticaForm
  - [x] codigo, descripcion
  - [x] proveedor_tipo, obra_social_id, monto_unitario

- [x] RegistroUsuarioForm
  - [x] username, password, password_confirm
  - [x] rol

- [x] CodigoForm
  - [x] numero, descripcion

**Archivos:**
- [x] `app/forms.py` - ✅ 9 formularios con validadores integrados

---

## ✅ TAREA 3: Documentación (COMPLETADO)

- [x] FASE3_VALIDACIONES.md - Guía completa de integración
- [x] FASE3_RESUMEN.md - Resumen ejecutivo
- [x] CHECKLIST (este archivo)

---

## 🟡 TAREA 4: Integración en Rutas (PENDIENTE)

### Rutas Pacientes
- [ ] `/pacientes/nuevo` (GET/POST)
  - [ ] Crear instancia de PacienteForm
  - [ ] Poblar localidades y obras sociales dinámicamente
  - [ ] Procesar form.validate_on_submit()
  - [ ] Guardar paciente con datos validados

- [ ] `/pacientes/<id>/editar` (GET/POST)
  - [ ] Crear instancia de PacienteForm
  - [ ] Pre-poblar con datos existentes
  - [ ] Procesar validaciones
  - [ ] Actualizar paciente

### Rutas Turnos
- [ ] `/turnos/nuevo` (GET/POST)
  - [ ] Crear instancia de TurnoForm
  - [ ] Validar turnos superpuestos (opcional)
  - [ ] Guardar turno

- [ ] `/turnos/<id>/editar` (GET/POST)
  - [ ] Crear instancia de TurnoForm
  - [ ] Pre-poblar campos
  - [ ] Actualizar turno

### Rutas Prestaciones
- [ ] `/prestaciones/nueva` (GET/POST)
  - [ ] Integrar PrestacionForm

- [ ] `/prestaciones/<id>/editar` (GET/POST)
  - [ ] Integrar PrestacionForm

### Rutas Finanzas/Gastos
- [ ] `/finanzas/gastos/nuevo` (GET/POST)
  - [ ] Integrar GastoForm

- [ ] `/finanzas/gastos/<id>/editar` (GET/POST)
  - [ ] Integrar GastoForm

### Rutas Obras Sociales
- [ ] Crear ruta `/obras-sociales/nueva` (GET/POST)
  - [ ] Integrar ObraSocialForm

- [ ] Crear ruta `/obras-sociales/<id>/editar` (GET/POST)
  - [ ] Integrar ObraSocialForm

### Rutas Prácticas
- [ ] Crear ruta `/practicas/nueva` (GET/POST)
  - [ ] Integrar PracticaForm

- [ ] Crear ruta `/practicas/<id>/editar` (GET/POST)
  - [ ] Integrar PracticaForm

### Rutas Códigos
- [ ] Crear ruta `/codigos/nuevo` (GET/POST)
  - [ ] Integrar CodigoForm

- [ ] Crear ruta `/codigos/<id>/editar` (GET/POST)
  - [ ] Integrar CodigoForm

### Rutas Usuarios
- [ ] `/login` (GET/POST)
  - [ ] Integrar LoginForm

- [ ] Crear ruta `/admin/usuarios/nuevo` (GET/POST)
  - [ ] Integrar RegistroUsuarioForm

---

## 🟡 TAREA 5: Testing (PENDIENTE)

### Testing Validadores
- [ ] Test ValidadorPaciente.validar_dni() con múltiples casos
- [ ] Test ValidadorTurno.validar_fecha() con fechas pasadas
- [ ] Test ValidadorTurno.validar_hora() fuera de rango
- [ ] Test ValidadorPrestacion.validar_monto() negativo
- [ ] Test ValidadorGasto.validar_categoria() inválida
- [ ] Test ValidadorObraSocial.validar_nombre() muy corto
- [ ] Test ValidadorPractica.validar_proveedor_tipo() inválido
- [ ] Test ValidadorUsuario.validar_password() muy corto
- [ ] Test ValidadorCodigo.validar_numero() muy largo
- [ ] Test ValidadorOdontograma.validar_numero_diente() fuera de rango

### Testing Formularios
- [ ] Test PacienteForm con datos válidos
- [ ] Test PacienteForm con datos inválidos
- [ ] Test TurnoForm con datos válidos
- [ ] Test TurnoForm con turno superpuesto
- [ ] Test PrestacionForm con monto negativo
- [ ] Test GastoForm con categoría inválida
- [ ] Test LoginForm con credenciales
- [ ] Test ObraSocialForm
- [ ] Test PracticaForm
- [ ] Test RegistroUsuarioForm con contraseñas no coincidentes
- [ ] Test CodigoForm

### Testing Integración en Rutas
- [ ] Test GET `/pacientes/nuevo` carga form vacío
- [ ] Test POST `/pacientes/nuevo` con datos válidos guarda
- [ ] Test POST `/pacientes/nuevo` con datos inválidos muestra errores
- [ ] Repetir para todas las demás rutas

---

## 📝 Notas de Implementación

### DNI Flexible Internacional
```python
# Aceptados:
- 8 dígitos (nacionales argentinos): 12345678 ✅
- 5 dígitos (extranjeros): 12345 ✅
- 6-10 dígitos (extranjeros): 123456-1234567890 ✅

# Rechazados:
- < 5 dígitos: 1234 ❌
- > 10 dígitos: 12345678901 ❌
- Caracteres no dígitos: 1234567A ❌
```

### Importes en Formularios
```python
# Todos los campos DecimalField con:
- Min 0.01 (no se permite 0)
- Max 999,999.99
- 2 decimales obligatorios

# Excepto donde sea opcional (descuentos pueden ser 0)
```

### Protección CSRF
```html
<!-- REQUERIDO en TODAS las plantillas de formularios -->
{{ form.hidden_tag() }}

<!-- SECRET_KEY debe estar configurado en app/__init__.py -->
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
```

### Select Fields Dinámicos
```python
# SIEMPRE poblar después de instanciar el formulario:
form.localidad_id.choices = [
    (0, '--- Seleccionar ---'),
    *[(loc.id, loc.nombre) for loc in Localidad.query.all()]
]

# NO dejar valores hard-coded
```

---

## 🎯 Prioridad de Integración Recomendada

### Fase 1 (Crítico): 3 rutas
1. `/pacientes/nuevo` - Ruta más usada
2. `/turnos/nuevo` - Ruta importante
3. `/login` - Ruta de autenticación

### Fase 2 (Alto): 3 rutas
4. `/pacientes/<id>/editar`
5. `/turnos/<id>/editar`
6. `/prestaciones/nueva`

### Fase 3 (Medio): 6 rutas
7. `/prestaciones/<id>/editar`
8. `/finanzas/gastos/nuevo`
9. `/finanzas/gastos/<id>/editar`
10. Obras Sociales (crear + editar)
11. Prácticas (crear + editar)
12. Códigos (crear + editar)

### Fase 4 (Opcional): 2 rutas
13. `/admin/usuarios/nuevo`
14. Cualquier otra ruta

---

## 📚 Archivos de Referencia

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| `app/services/common/validators.py` | 11 validadores, 40+ métodos | ✅ Completado |
| `app/forms.py` | 9 formularios WTF | ✅ Completado |
| `docs/FASE3_VALIDACIONES.md` | Guía de integración | ✅ Completado |
| `docs/FASE3_RESUMEN.md` | Resumen ejecutivo | ✅ Completado |
| `docs/decisiones_tecnicas.md` | Arquitectura general | ✅ Ref. Importante |

---

## ✨ Características Finalizadas

✅ DNI flexible (5-10 dígitos, internacional)  
✅ 40+ métodos de validación  
✅ 9 formularios WTF con CSRF automático  
✅ Mensajes de error en español  
✅ Validadores custom integrados  
✅ Select fields dinámicos soportados  
✅ Documentación completa con ejemplos  

---

## 🚀 Próximos Pasos

1. **EMPEZAR:** Integrar PacienteForm en `/pacientes/nuevo`
   - Referencia: [FASE3_VALIDACIONES.md](FASE3_VALIDACIONES.md#-cómo-integrar-validaciones-en-las-rutas)
   
2. **LUEGO:** Integrar TurnoForm en `/turnos/nuevo`

3. **DESPUÉS:** Completar remaining 16 rutas según prioridad

---

**Responsable actual:** GitHub Copilot  
**Última revisión:** Diciembre 2025  
**Próxima revisión:** Después de integración de Pacientes
