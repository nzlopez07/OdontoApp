# Validaciones de Turnos - Sistema OdontoApp

## Resumen de Validaciones Implementadas

El sistema ahora cuenta con validaciones completas para la creación y actualización de turnos, garantizando la integridad de los datos y evitando conflictos de horarios.

---

## 1. Matriz de Transiciones de Estado

### Estados Disponibles
- **Pendiente**: Estado inicial del turno
- **Confirmado**: Turno confirmado por el paciente
- **Atendido**: Turno completado exitosamente
- **NoAtendido**: Paciente no asistió
- **Cancelado**: Turno cancelado

### Transiciones Válidas

```
Pendiente → Confirmado, Cancelado, NoAtendido
Confirmado → Atendido, NoAtendido, Cancelado
Atendido → [ESTADO FINAL - No se puede cambiar]
NoAtendido → [ESTADO FINAL - No se puede cambiar]
Cancelado → [ESTADO FINAL - No se puede cambiar]
```

### Ejemplos de Validación de Estados

#### ✅ Transiciones Válidas
- Pendiente → Confirmado ✓
- Confirmado → Atendido ✓
- Pendiente → Cancelado ✓

#### ❌ Transiciones Inválidas
- Atendido → Pendiente ✗ (Estado final)
- NoAtendido → Confirmado ✗ (Estado final)
- Cancelado → Atendido ✗ (Estado final)
- Pendiente → Atendido ✗ (Debe pasar por Confirmado primero)

---

## 2. Validación de Solapamiento de Horarios

### Algoritmo de Detección
El sistema verifica solapamientos considerando:
- Fecha del turno
- Hora de inicio
- Duración en minutos
- Turnos existentes en la misma fecha

### Fórmula de Solapamiento
Dos turnos se solapan si:
```
inicio1 < fin2 AND inicio2 < fin1
```

### Ejemplos de Solapamiento

#### Caso 1: Solapamiento Total
```
Turno existente: 10:00 - 11:00 (60 min)
Nuevo turno:     10:00 - 11:00 (60 min)
Resultado: ❌ RECHAZADO - Solapamiento total
```

#### Caso 2: Solapamiento Parcial
```
Turno existente: 10:00 - 11:00 (60 min)
Nuevo turno:     10:30 - 11:30 (60 min)
Resultado: ❌ RECHAZADO - Solapamiento de 30 minutos
```

#### Caso 3: Sin Solapamiento (Consecutivos)
```
Turno existente: 10:00 - 11:00 (60 min)
Nuevo turno:     11:00 - 12:00 (60 min)
Resultado: ✅ ACEPTADO - No hay solapamiento
```

#### Caso 4: Duraciones Variables
```
Turno existente: 12:15 - 13:45 (90 min)
Nuevo turno:     13:00 - 14:00 (60 min)
Resultado: ❌ RECHAZADO - Solapamiento de 45 minutos
```

#### Caso 5: Turno Corto dentro de Turno Largo
```
Turno existente: 14:00 - 16:00 (120 min)
Nuevo turno:     14:30 - 15:00 (30 min)
Resultado: ❌ RECHAZADO - Turno completamente dentro de otro
```

---

## 3. Validaciones de Creación de Turnos

### 3.1 Validaciones de Datos Básicos
- ✓ Paciente requerido y existente
- ✓ Fecha requerida
- ✓ Hora requerida
- ✓ Duración válida (5-480 minutos)

### 3.2 Validaciones de Fecha
- ❌ No permitir turnos en fechas pasadas
- ❌ Solo lunes a sábado (días laborables)

### 3.3 Validaciones de Horario
- ✓ Horario de atención: 08:00 - 21:00
- ❌ No permitir turnos fuera del horario
- ❌ No permitir que el turno termine después de las 21:00

### 3.4 Ejemplos de Validación de Horario

#### Caso 1: Turno que excede horario de cierre
```
Hora inicio: 20:30
Duración: 60 minutos
Hora fin calculada: 21:30
Resultado: ❌ RECHAZADO
Mensaje: "El turno terminaría a las 21:30, después del horario de atención (21:00)"
```

#### Caso 2: Turno válido al final del día
```
Hora inicio: 20:30
Duración: 30 minutos
Hora fin calculada: 21:00
Resultado: ✅ ACEPTADO
```

#### Caso 3: Turno en domingo
```
Fecha: 2025-12-21 (Domingo)
Resultado: ❌ RECHAZADO
Mensaje: "Solo se pueden crear turnos de lunes a sábado"
```

---

## 4. Reglas Especiales para Turnos Pasados

### Comportamiento
Los turnos de fechas pasadas tienen restricciones adicionales:
- Solo pueden cambiar a estados: **Atendido** o **NoAtendido**
- No se pueden cambiar a: Pendiente, Confirmado, Cancelado

### Ejemplo
```
Turno: 2025-12-15 10:00 (fecha pasada)
Estado actual: Pendiente
Intentar cambiar a: Confirmado
Resultado: ❌ RECHAZADO
Mensaje: "Los turnos de fechas pasadas solo pueden marcarse como 'Atendido' o 'NoAtendido'"
```

---

## 5. Interfaz de Usuario

### Formulario de Cambio de Estado
El formulario en la página de detalle del turno ahora:
- ✅ Solo muestra estados válidos según el estado actual
- ✅ Deshabilita el botón si no hay transiciones permitidas
- ✅ Muestra mensaje informativo para estados finales

### Mensajes de Error Mejorados
Todos los errores de validación muestran mensajes claros:
- Indica qué regla se violó
- Sugiere transiciones válidas cuando aplique
- Muestra detalles de turnos solapados (hora, paciente)

---

## 6. Casos de Prueba Sugeridos

### Prueba 1: Crear Turno con Solapamiento
1. Crear turno: 2025-12-23 10:00 (60 min)
2. Intentar crear: 2025-12-23 10:30 (60 min)
3. Verificar mensaje de error con detalles del turno existente

### Prueba 2: Transiciones de Estado Inválidas
1. Crear turno en estado "Pendiente"
2. Cambiarlo a "Atendido" directamente
3. Verificar que se rechaza (debe pasar por Confirmado)

### Prueba 3: Estado Final
1. Cambiar turno a "Atendido"
2. Intentar cambiar a cualquier otro estado
3. Verificar que el select está deshabilitado

### Prueba 4: Turno que Excede Horario
1. Intentar crear turno: 20:30 (90 min)
2. Verificar rechazo (terminaría a las 22:00)

### Prueba 5: Duración Variable
1. Crear turno: 12:15 (90 min)
2. Intentar crear: 13:30 (30 min)
3. Verificar que se detecta el solapamiento de 15 minutos

---

## 7. Código de Ejemplo

### Verificar Solapamiento Manualmente
```python
from app.services.turno_service import TurnoService
from datetime import date, time

# Verificar si hay solapamiento
hay_solape, mensaje, turnos = TurnoService.verificar_solapamiento(
    fecha=date(2025, 12, 23),
    hora_inicio=time(10, 30),
    duracion=60
)

if hay_solape:
    print(f"Error: {mensaje}")
    for turno in turnos:
        print(f"- {turno}")
```

### Validar Transición de Estado
```python
from app.services.turno_service import TurnoService

# Validar transición
es_valida, mensaje = TurnoService.validar_transicion_estado(
    estado_actual='Pendiente',
    estado_nuevo='Atendido'
)

if not es_valida:
    print(f"Transición inválida: {mensaje}")
```

---

## 8. Mensajes de Error Completos

### Error de Solapamiento
```
El horario se solapa con 1 turno(s) existente(s): 
10:00-11:00 (Juan Pérez)
```

### Error de Transición Inválida
```
No se puede cambiar de "Pendiente" a "Atendido". 
Transiciones permitidas: Confirmado, Cancelado, NoAtendido
```

### Error de Estado Final
```
El turno está en estado "Atendido" (final). 
No se pueden hacer cambios de estado.
```

### Error de Horario
```
El turno terminaría a las 21:30, después del horario de atención (21:00). 
Reduzca la duración o elija un horario más temprano.
```

---

## 9. Checklist de Validaciones ✓

- [x] Matriz de transiciones de estado implementada
- [x] Detección de solapamientos con duración variable
- [x] Validación de horarios de atención
- [x] Validación de días laborables
- [x] Restricciones para turnos pasados
- [x] Validación de duración (5-480 min)
- [x] Mensajes de error descriptivos
- [x] UI con estados permitidos dinámicos
- [x] Manejo de excepciones en rutas
- [x] Estados finales no modificables

---

**Última actualización:** 20 de diciembre de 2025
