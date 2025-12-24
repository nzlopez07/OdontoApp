# 🗺️ Roadmap de Calidad — OdontoApp

**Proyecto:** Sistema de Gestión de Consultorio Odontológico
**Objetivo:** elevar el sistema a estándar **profesional, seguro y mantenible**, apto para uso real con datos clínicos sensibles.

---

## 🎯 Principios rectores

* Arquitectura en capas (routes / services / models)
* Datos clínicos **local-first** (propiedad del consultorio)
* Principio de mínimo privilegio (*Least Privilege*)
* Ningún update sin backup previo
* Logs técnicos **sin datos sensibles**
* Evolución sin romper datos (*Backward compatibility*)

---

## 🧱 FASE 0 — Preparación del proyecto (contexto para Copilot) ✅

**Objetivo:** dejar el proyecto listo para trabajar de forma ordenada y consistente.

* [x] Crear carpeta `/docs`
* [x] Crear archivos:

  * `docs/roadmap.md` ✅
  * `docs/decisiones_tecnicas.md` ✅
  * `docs/seguridad.md` ✅
  * `docs/DOCUMENTACION_COMPLETA.md` ✅
  * `docs/ANALISIS_MIGRACION_FRONTEND.md` ✅
* [x] Documentar decisiones técnicas clave (arquitectura, DB local, roles, backups)
* [x] Decisión Frontend: **Mantener Jinja2 + agregar HTMX** (no migrar a React/Vue)

> 📌 Esta fase mejora notablemente la calidad de las sugerencias de Copilot.

**Estado:** ✅ **COMPLETADA** (Diciembre 2025)

---

## 🔐 FASE 1 — Autenticación

**Prioridad:** 🔴 CRÍTICA

**Objetivo:** impedir acceso no autorizado al sistema.

* [x] Crear modelo `Usuario`
  * id
  * username
  * password_hash
  * role
  * activo
* [x] Implementar login/logout
* [x] Hash de contraseñas (`werkzeug.security`)
* [x] Manejo de sesión con `Flask-Login`
* [x] Proteger todas las rutas internas

**Conceptos:** Authentication, Password Hashing, Session Management

**Estado:** ✅ **COMPLETADA** (Diciembre 2025)

---

## 🧑‍⚕️ FASE 2 — Autorización por roles

**Objetivo:** controlar qué puede hacer cada usuario.

Roles implementados:

* `DUEÑA` (Florencia López) - Acceso completo: clínico + finanzas
* `ODONTOLOGA` - Solo funciones clínicas (sin finanzas)
* `ADMIN` - Panel técnico (logs, BD, backups) - sin datos clínicos

* [x] Definir roles de forma centralizada
* [x] Crear métodos de autorización en modelo Usuario
* [x] Restringir acceso a datos clínicos según rol
* [x] Asegurar que `ADMIN` no vea pacientes ni operaciones
* [x] Implementar vista de finanzas (solo para DUEÑA)

**Conceptos:** Authorization, RBAC, Least Privilege

**Estado:** ✅ **COMPLETADA** (Diciembre 2025)

---

## 🧪 FASE 3 — Validaciones formales

**Objetivo:** evitar datos inválidos o inconsistentes.

* [x] Integrar `Flask-WTF`
* [x] Validar:

  * DNI
  * Fechas
  * Montos
  * Turnos superpuestos (en progreso)
* [x] Centralizar reglas de negocio en `services/`

**Validadores implementados:**
- `ValidadorPaciente`: DNI, nombre, apellido, teléfono
- `ValidadorTurno`: fecha, hora, duración
- `ValidadorPrestacion`: monto, descuentos
- `ValidadorGasto`: categoría, monto, descripción
- `ValidadorFecha`: fechas de nacimiento, rangos

**Formularios WTF completados:**
- [x] `PacienteForm`: crear/editar pacientes
- [x] `TurnoForm`: crear/editar turnos con autocomplete
- [x] `PrestacionForm`: crear/editar prestaciones con estilo factura
- [x] `GastoForm`: crear/editar gastos
- [x] `LoginForm`: autenticación

**Mejoras UX implementadas (Diciembre 2025):**
- [x] Autocomplete en selectores de paciente (búsqueda sensible a acentos)
- [x] Formato estándar: "Nombre Apellido (DNI: XXXXX)"
- [x] Normalización de texto con NFD para búsquedas sin tildes
- [x] Pre-carga de paciente desde URL (?paciente_id=X)
- [x] Auto-carga de prácticas cuando paciente está pre-seleccionado
- [x] Validación JavaScript para bloqueo de caracteres inválidos
- [x] Preservación de datos tras errores de validación
- [x] Template factura con tabla de prácticas, subtotal, descuentos y total

**Conceptos:** Input Validation, Business Rules, Progressive Enhancement

**Estado:** ✅ **COMPLETADA** (Diciembre 2025)

---

## 💰 FASE 3.5 — Dashboard Financiero Avanzado

**Objetivo:** proporcionar visibilidad clara de ingresos por fuente de pago, distinguiendo entre cobros inmediatos (Particular) y diferidos (Obras Sociales).

**Motivación:** Las obras sociales (IPSS, SANCOR SALUD) tienen tiempos de pago diferentes a los pacientes particulares, por lo que es crucial poder analizar cada fuente por separado para mantener control financiero.

**Implementado:**
- [x] Tarjetas de resumen por fuente de pago (Particular, IPSS, SANCOR SALUD, etc.)
- [x] Visualización de total e cantidad de prestaciones por fuente
- [x] Gráfico dinámico según filtro:
  - **"Todo"**: distribución por fuente de pago (torta)
  - **Obra social específica**: distribución por práctica (torta)
- [x] Tabla de detalle de prestaciones por obra social
  - Fecha | Paciente | Prácticas (códigos) | Monto
  - Muestra últimas 100 prestaciones
  - Total al pie de la tabla
- [x] Eliminación de filtro por paciente individual (no necesario)
- [x] Filtros mantenidos: Período + Obra Social

**Servicios agregados:**
- `ObtenerEstadisticasFinanzasService.obtener_ingresos_por_tipo()`: resumen por fuente
- `ObtenerEstadisticasFinanzasService.obtener_detalle_prestaciones()`: detalle transaccional

**Conceptos:** Financial Reporting, Cash Flow Management, Business Intelligence

**Estado:** ✅ **COMPLETADA** (Diciembre 2025)

---

## 🧾 FASE 4 — Logging técnico seguro

**Objetivo:** soporte remoto sin comprometer datos clínicos.

* [x] Configurar logging estructurado con múltiples archivos
* [x] Niveles: DEBUG / INFO / WARNING / ERROR
* [x] Excluir datos sensibles de los logs (SanitizingFormatter)
* [x] Implementar vista de admin para visualización de logs
* [x] Filtros por tipo, nivel, búsqueda y cantidad de líneas
* [x] Descarga de archivos de log completos
* [x] Helpers de logging seguros (log_helpers.py)

**Archivos de Log implementados:**
- `logs/app.log` - Log principal de la aplicación (10 MB rotación, 10 backups)
- `logs/errors.log` - Solo errores y excepciones
- `logs/security.log` - Eventos de autenticación y permisos
- `logs/whatsapp.log` - Integración con WhatsApp

**Helpers de logging seguros:**
- `log_paciente_event()` - Eventos de pacientes (solo IDs, sin nombres/DNI)
- `log_turno_event()` - Eventos de turnos (sin datos personales)
- `log_prestacion_event()` - Eventos de prestaciones (monto solo en creación/eliminación)
- `log_security_event()` - Login, logout, accesos denegados
- `log_whatsapp_event()` - Mensajes WhatsApp (teléfonos enmascarados)
- `log_database_event()` - Backups, migraciones, operaciones de BD
- `log_error()` - Excepciones con contexto técnico

**Vista de Admin (/admin/logs):**
- Selector de tipo de log (app/security/whatsapp/errors)
- Filtro por nivel (DEBUG/INFO/WARNING/ERROR)
- Búsqueda de texto
- Selector de cantidad de líneas (100-5000)
- Descarga de log completo
- Interfaz estilo terminal con colores por nivel
- Auto-actualización con filtros persistentes

**Conceptos:** Application Logging, Sanitized Logs, Log Rotation, Remote Support

**Estado:** ✅ **COMPLETADA** (Diciembre 2025)

---

## ⏱️ FASE 5 — Scheduler (tareas automáticas)

**Objetivo:** mantener consistencia del sistema sin depender del uso manual.

* [x] Integrar APScheduler
* [x] Mover actualización de turnos vencidos a tarea programada (cada 5 min)
* [x] Configurar frecuencia segura (5 min) y cleanup de conversaciones

**Conceptos:** Background Jobs, Scheduled Tasks

---

## 🧪 FASE 6 — Testing estratégico

**Objetivo:** poder actualizar el sistema con confianza.

**Estado:** 🟡 **EN PROGRESO** (Diciembre 2025)

Cobertura implementada (servicios):

- Finanzas: resumen, ingresos por tipo/práctica, egresos por categoría, detalle por obra social, evolución mensual.
- Gasto: creación con validaciones y listado con filtros/orden.
- Prestación: correcciones de `listar_prestaciones` (filtrado/orden por `fecha`).

Cobertura implementada (rutas):

- Finanzas: dashboard, gastos (listar/crear), reportes, API de resumen.
- Pacientes: listado, creación por formulario, detalle.
- Turnos: agenda, formulario de creación (GET), cambio de estado.
- Prácticas: listado y creación con obra social.
- Prestaciones: listado por paciente y creación con `practica_ids[]`.
- Admin: acceso al dashboard bajo `LOGIN_DISABLED` en testing; visualización de logs.

Herramienta:

* `pytest`

Tests adicionales recomendados (pendientes):

- Editar/eliminar en rutas de pacientes, turnos y prácticas.
- Endpoints de odontograma y flujos asociados.
- Backup y restore end-to-end.
- Reducir warnings legacy de SQLAlchemy (`Query.get`) migrando a `Session.get`.

**Conceptos:** Unit Testing, Regression Testing

---

## 📦 FASE 7 — Empaquetado como aplicación de escritorio

**Objetivo:** facilitar instalación, uso y soporte remoto.

* [ ] Empaquetar con PyInstaller (primera versión)
* [ ] BD local incluida
* [ ] Logs locales
* [ ] Versión visible en la app

**Conceptos:** Desktop Packaging, Local-first App

---

## 🔄 FASE 8 — Sistema de updates seguros

**Objetivo:** poder corregir errores y mejorar el sistema sin riesgo.

* [ ] Versionado semántico (vX.Y.Z)
* [ ] Backup automático previo a cada update
* [ ] Script de actualización asistida
* [ ] Compatibilidad con datos existentes

**Regla de oro:** ❗ Nunca actualizar sin backup

---

## 📋 CHECKLIST GENERAL

```text
[x] Fase 0 – Preparación ✅
[x] Fase 1 – Autenticación ✅
[x] Fase 2 – Autorización ✅
[x] Fase 3 – Validaciones ✅
[x] Fase 3.5 – Dashboard Financiero Avanzado ✅
[x] Fase 4 – Logging ✅
[x] Fase 5 – Scheduler ✅
[~] Fase 6 – Tests (avance sustancial)
[ ] Fase 7 – Packaging
[ ] Fase 8 – Updates
```

---

## 📊 Resumen de Estado del Proyecto (Diciembre 2025)

### ✅ Funcionalidades Core Completadas

**Gestión Clínica:**
- Sistema de pacientes completo (CRUD + búsqueda)
- Agenda de turnos con estados y cambios automáticos
- Prestaciones con múltiples prácticas y descuentos
- Odontograma digital interactivo
- Conversaciones por WhatsApp (integración Meta API)

**Gestión Administrativa:**
- Dashboard financiero con análisis por fuente de pago
- Control de gastos por categoría
- Reportes anuales de evolución
- Sistema de obras sociales y códigos de prácticas
 - Botón en Admin: **Ejecutar Tests** (ejecuta `pytest` en background y muestra resultados en logs)

**Seguridad y UX:**
- Autenticación y autorización por roles (DUEÑA/ODONTOLOGA/ADMIN)
- Validaciones robustas con Flask-WTF
- Autocomplete en formularios con búsqueda sensible a acentos
- Interfaz factura para prestaciones
- Pre-carga de datos desde enlaces contextuales

**Arquitectura:**
- Patrón MVC + Services
- SQLAlchemy ORM con SQLite
- Scheduler para tareas automáticas
- Rate limiting para APIs externas
- Backups automáticos antes de operaciones destructivas

### 🟡 Próximas Prioridades

1. **Testing estratégico** (Fase 6) - Completar cobertura: editar/eliminar y odontograma; reducir warnings SQLAlchemy
2. **Logging mejorado** (Fase 4) - Afinar filtros y auto-actualización
3. **Empaquetado** (Fase 7) - Distribución como app de escritorio
4. **Updates seguros** (Fase 8) - Sistema de actualización con backups automáticos

---

## 🧠 Nota final

Este roadmap está diseñado para:

* trabajar eficientemente con GitHub Copilot
* evitar decisiones técnicas incorrectas
* entregar un software **ético, seguro y profesional**

> Un sistema clínico pequeño **no es un sistema simple**: es un sistema sensible.
