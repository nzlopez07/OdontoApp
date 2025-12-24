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

* [ ] Integrar `Flask-WTF`
* [ ] Validar:

  * DNI
  * Fechas
  * Montos
  * Turnos superpuestos
* [ ] Centralizar reglas de negocio en `services/`

**Conceptos:** Input Validation, Business Rules

---

## 🧾 FASE 4 — Logging técnico seguro

**Objetivo:** soporte remoto sin comprometer datos clínicos.

* [ ] Configurar logging estructurado
* [ ] Niveles: INFO / WARNING / ERROR
* [ ] Excluir datos sensibles de los logs
* [ ] Implementar exportación de diagnóstico técnico

**Conceptos:** Application Logging, Sanitized Logs

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

Tests mínimos recomendados:

* [ ] Crear paciente
* [ ] Crear turno
* [ ] Cambio automático a NoAtendido
* [ ] Cambio de estado manual
* [ ] Backup y restore

Herramienta:

* `pytest`

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
[x] Fase 1 – Autenticación
[x] Fase 2 – Autorización
[ ] Fase 3 – Validaciones
[ ] Fase 4 – Logging
[x] Fase 5 – Scheduler
[ ] Fase 6 – Tests
[ ] Fase 7 – Packaging
[ ] Fase 8 – Updates
```

---

## 🧠 Nota final

Este roadmap está diseñado para:

* trabajar eficientemente con GitHub Copilot
* evitar decisiones técnicas incorrectas
* entregar un software **ético, seguro y profesional**

> Un sistema clínico pequeño **no es un sistema simple**: es un sistema sensible.
