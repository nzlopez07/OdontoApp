# 🧪 Guía de Pruebas - Agenda de Turnos

## ✅ Checklist de Implementación Completada

### Estructura de Carpetas
- ✅ `app/routes/turnos.py` - Rutas actualizadas
- ✅ `app/services/turno_service.py` - Servicio mejorado
- ✅ `app/templates/turnos/agenda.html` - Nueva plantilla
- ✅ `app/templates/turnos/ver.html` - Nueva plantilla

### Funcionalidades Implementadas
- ✅ Vista de agenda semanal (Lunes a Sábado)
- ✅ Horarios de 08:00 a 21:00 (slots de 30 minutos)
- ✅ Navegación entre semanas
- ✅ Vista de detalles de turno
- ✅ Colores por estado
- ✅ Links clickeables
- ✅ Información del paciente
- ✅ Cambio de estado de turno
- ✅ Historial de cambios

---

## 🚀 Pruebas Funcionales

### Test 1: Acceso a la Agenda
**Objetivo:** Verificar que la página de agenda se carga correctamente

**Pasos:**
1. Abrir navegador en `http://localhost:5000/turnos`
2. Esperar a que cargue la página

**Resultado Esperado:**
- ✅ Se muestra una tabla con 6 columnas (Lunes-Sábado)
- ✅ Header muestra los días de la semana con fechas
- ✅ Se ven todos los turnos de la semana actual
- ✅ Botones de navegación en la parte superior

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 2: Navegación de Semanas
**Objetivo:** Verificar que la navegación entre semanas funciona

**Pasos:**
1. En la página de agenda, hacer click en "Semana Siguiente >"
2. Verificar que las fechas cambien
3. Hacer click en "< Semana Anterior"
4. Verificar que vuelva a las fechas originales

**Resultado Esperado:**
- ✅ Las fechas en el header cambian correctamente
- ✅ Los turnos mostrados corresponden a la semana seleccionada
- ✅ Los botones de navegación están activos/desactivos según corresponda

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 3: Navegación por URL
**Objetivo:** Verificar que se puede acceder a una semana específica via URL

**Pasos:**
1. Ir a `http://localhost:5000/turnos?fecha_inicio=2025-12-22`
2. Verificar que muestre esa semana

**Resultado Esperado:**
- ✅ Se muestra la agenda de la semana comenzando en 22/12/2025
- ✅ Las fechas coinciden con el parámetro

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 4: Click en Turno
**Objetivo:** Verificar que hacer click en un turno muestra sus detalles

**Pasos:**
1. En la página de agenda, hacer click en cualquier tarjeta de turno
2. Esperar a que cargue la página de detalles

**Resultado Esperado:**
- ✅ Se redirige a `/turnos/<turno_id>`
- ✅ Se muestran todos los detalles del turno
- ✅ Se ve el nombre del paciente
- ✅ Se muestra el estado actual

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 5: Cambio de Estado
**Objetivo:** Verificar que se puede cambiar el estado del turno

**Pasos:**
1. En la página de detalles del turno, cambiar el estado en el dropdown
2. Hacer click en "Actualizar"
3. Verificar que el estado cambió

**Resultado Esperado:**
- ✅ El estado se actualiza en la base de datos
- ✅ Se muestra un mensaje de éxito
- ✅ El nuevo estado aparece en la página

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 6: Historial de Cambios
**Objetivo:** Verificar que se muestra el historial de cambios de estado

**Pasos:**
1. Hacer varios cambios de estado en un turno
2. Volver a la página de detalles
3. Ver la sección "Historial de Cambios"

**Resultado Esperado:**
- ✅ Se lista todos los cambios de estado realizados
- ✅ Se muestra la fecha y hora de cada cambio
- ✅ Se muestra el estado resultante de cada cambio

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 7: Colores de Estados
**Objetivo:** Verificar que los colores correspondan a los estados

**Pasos:**
1. Crear varios turnos con diferentes estados
2. Visualizarlos en la agenda

**Resultado Esperado:**
- ✅ Pendiente → Amarillo (#ffc107)
- ✅ Confirmado → Cyan (#0dcaf0)
- ✅ Atendido → Verde (#198754)
- ✅ NoAtendido → Rojo (#dc3545)
- ✅ Cancelado → Gris (#6c757d)

**Resultado Actual:**
```
Pendiente:    [ ] Amarillo [ ] Otro color: ___________
Confirmado:   [ ] Cyan     [ ] Otro color: ___________
Atendido:     [ ] Verde    [ ] Otro color: ___________
NoAtendido:   [ ] Rojo     [ ] Otro color: ___________
Cancelado:    [ ] Gris     [ ] Otro color: ___________
```

---

### Test 8: Link a Ficha del Paciente
**Objetivo:** Verificar que se puede acceder a la ficha del paciente desde el turno

**Pasos:**
1. En la página de detalles del turno, hacer click en "Ver Ficha del Paciente"
2. Verificar que se muestra la página del paciente

**Resultado Esperado:**
- ✅ Se redirige a `/pacientes/<paciente_id>`
- ✅ Se muestran todos los datos del paciente

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 9: Eliminar Turno
**Objetivo:** Verificar que se puede eliminar un turno Pendiente

**Pasos:**
1. Crear un nuevo turno (estado: Pendiente)
2. Ir a su página de detalles
3. Hacer click en "Eliminar Turno"
4. Confirmar la eliminación

**Resultado Esperado:**
- ✅ El turno se elimina de la base de datos
- ✅ Se redirige a la agenda
- ✅ El turno no aparece más en la agenda

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 10: Responsive Design
**Objetivo:** Verificar que la agenda se ve bien en diferentes tamaños de pantalla

**Pasos Tablet:**
1. Abrir en tablet o usar DevTools con ancho 768px
2. Verificar que la tabla sea scrolleable horizontalmente
3. Verificar que los textos sean legibles

**Pasos Móvil:**
1. Abrir en móvil o usar DevTools con ancho 375px
2. Verificar que la tabla sea scrolleable horizontalmente
3. Verificar que los textos sean legibles con fuente pequeña

**Resultado Esperado:**
- ✅ Desktop (>1024px): 6 columnas visibles sin scroll
- ✅ Tablet (768-1024px): 6 columnas con scroll horizontal
- ✅ Móvil (<768px): 6 columnas con scroll horizontal, fuente reducida

**Resultado Actual - Desktop:**
```
[ ] PASS - [ ] FAIL
```

**Resultado Actual - Tablet:**
```
[ ] PASS - [ ] FAIL
```

**Resultado Actual - Móvil:**
```
[ ] PASS - [ ] FAIL
```

---

## 🐛 Pruebas de Casos Límite

### Test 11: Agenda Vacía
**Objetivo:** Verificar comportamiento cuando no hay turnos

**Pasos:**
1. Ir a una semana sin turnos
2. Verificar que la agenda se cargue correctamente

**Resultado Esperado:**
- ✅ Se muestra la tabla completa sin errores
- ✅ Todas las celdas están vacías
- ✅ Los horarios siguen siendo visibles

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 12: Turno sin Detalles
**Objetivo:** Verificar que los turnos sin detalles se muestren correctamente

**Pasos:**
1. Crear un turno sin información en el campo "detalles"
2. Visualizarlo en la agenda y en detalles

**Resultado Esperado:**
- ✅ Se muestra correctamente en la agenda
- ✅ En la página de detalles, la sección se oculta/está vacía

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 13: Múltiples Turnos Mismo Horario
**Objetivo:** Verificar que se muestren correctamente múltiples turnos en la misma celda

**Pasos:**
1. Crear dos turnos a la misma hora en el mismo día
2. Visualizarlos en la agenda

**Resultado Esperado:**
- ✅ Ambas tarjetas de turno aparecen en la misma celda
- ✅ Se pueden hacer click en ambas independientemente

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

### Test 14: Turno Fuera de Horario
**Objetivo:** Verificar comportamiento de turnos fuera de horario

**Pasos:**
1. Crear un turno a las 06:00 (antes de horario)
2. Crear un turno a las 23:00 (después de horario)
3. Visualizar en agenda

**Resultado Esperado:**
- ✅ El turno de 06:00 no aparece
- ✅ El turno de 23:00 no aparece
- ✅ No hay errores en la página

**Resultado Actual:**
```
[ ] PASS
[ ] FAIL - Describa el error:
```

---

## 📊 Resumen de Pruebas

| # | Test | Resultado | Observaciones |
|---|------|-----------|---------------|
| 1 | Acceso a Agenda | [ ] | |
| 2 | Navegación Semanas | [ ] | |
| 3 | Navegación por URL | [ ] | |
| 4 | Click en Turno | [ ] | |
| 5 | Cambio de Estado | [ ] | |
| 6 | Historial de Cambios | [ ] | |
| 7 | Colores de Estados | [ ] | |
| 8 | Link Ficha Paciente | [ ] | |
| 9 | Eliminar Turno | [ ] | |
| 10 | Responsive Design | [ ] | |
| 11 | Agenda Vacía | [ ] | |
| 12 | Turno sin Detalles | [ ] | |
| 13 | Múltiples Turnos | [ ] | |
| 14 | Turno Fuera Horario | [ ] | |

**Total Pruebas:** 14
**Pasadas:** __/14
**Fallidas:** __/14

---

## 🔧 Troubleshooting

### Error: "Turno no encontrado"
**Causa:** El turno_id en la URL no existe
**Solución:** Verificar que el ID es válido

### Error: "Semana Siguiente/Anterior no funciona"
**Causa:** La ruta no recibe el parámetro
**Solución:** Verificar que la URL incluya `?fecha_inicio=YYYY-MM-DD`

### Tabla no se ve bien
**Causa:** Pantalla pequeña o navegador estrecho
**Solución:** Hacer scroll horizontal o ampliar ventana

### Turnos no aparecen en agenda
**Causa:** Los turnos están fuera del rango Lunes-Sábado
**Solución:** Verificar las fechas y el día de la semana

---

## 📝 Notas

- Asegúrese de que la base de datos esté poblada con datos de prueba
- Los turnos deben tener una fecha y hora válidas
- El paciente del turno debe existir en la base de datos
- Los cambios de estado se guardan automáticamente en la tabla de auditoría

---

**Documento creado:** 20/12/2025
**Última actualización:** 20/12/2025
