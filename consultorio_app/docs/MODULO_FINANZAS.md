# Módulo de Finanzas - OdontoApp

**Fecha de creación:** Diciembre 2025  
**Estado:** ✅ Completado  
**Acceso:** Solo usuarios con rol DUEÑA

---

## 📊 Visión General

El módulo de finanzas proporciona control integral sobre la gestión económica del consultorio, permitiendo:

- **Seguimiento de Ingresos**: Visualización de cobros por prestaciones realizadas
- **Registro de Egresos**: Gestión de gastos operativos categorizados
- **Balance Financiero**: Cálculo automático de rentabilidad
- **Reportes Temporales**: Análisis semanal, mensual y anual
- **Filtros Avanzados**: Por tipo de operación, paciente, categoría y período

---

## 🏗️ Arquitectura

### Modelos

**`app/models/gasto.py`**
```python
class Gasto(db.Model):
    id: int
    descripcion: str              # Descripción del gasto
    monto: Decimal                # Monto (usando Decimal para precisión)
    fecha: date                   # Fecha del gasto
    categoria: str                # MATERIAL, INSUMO, MATRICULA, CURSO, OPERATIVO, OTRO
    observaciones: str (opcional) # Detalles adicionales
    comprobante: str (opcional)   # Ruta del comprobante
    fecha_creacion: datetime      # Timestamp de creación
    creado_por_id: int            # FK a Usuario
```

**Relaciones:**
- `creado_por` → Usuario (many-to-one)

**Categorías de Gastos:**
- `MATERIAL`: Herramientas, equipos odontológicos
- `INSUMO`: Materiales de uso diario (guantes, algodón, anestésicos)
- `MATRICULA`: Matrículas profesionales
- `CURSO`: Capacitaciones, cursos de actualización
- `OPERATIVO`: Alquiler, servicios, impuestos
- `OTRO`: Gastos misceláneos

---

### Servicios

**`app/services/gasto/`**

#### `crear_gasto_service.py`
- **Método:** `CrearGastoService.crear()`
- **Parámetros:**
  - `descripcion`: str (requerido)
  - `monto`: float (requerido, > 0)
  - `fecha`: date (requerido)
  - `categoria`: str (requerido, debe ser una de las 6 categorías válidas)
  - `creado_por_id`: int (requerido)
  - `observaciones`: str (opcional)
  - `comprobante`: str (opcional)
- **Validaciones:**
  - Descripción no vacía
  - Monto mayor a 0
  - Categoría válida
  - Usuario existe
- **Retorna:** Objeto Gasto creado
- **Excepciones:** `OdontoAppError` con códigos específicos

#### `listar_gastos_service.py`
- **Método:** `ListarGastosService.listar()`
- **Parámetros opcionales:**
  - `fecha_desde`: date
  - `fecha_hasta`: date
  - `categoria`: str
- **Retorna:** Lista de Gastos ordenados por fecha descendente

#### `obtener_estadisticas_finanzas_service.py`
Contiene múltiples métodos para análisis financiero:

**`obtener_resumen()`**
- Calcula ingresos totales (suma de Prestacion.monto_total)
- Calcula egresos totales (suma de Gasto.monto)
- Calcula balance (ingresos - egresos)
- Soporta filtros: fecha_desde, fecha_hasta, paciente_id

**`obtener_ingresos_por_tipo()`**
- Agrupa ingresos por tipo de pago (Obra Social, Particular, etc.)
- Retorna lista con tipo, total y cantidad de operaciones

**`obtener_egresos_por_categoria()`**
- Agrupa egresos por categoría de gasto
- Retorna lista con categoría, total y cantidad

**`obtener_evolucion_mensual(anio)`**
- Genera reporte mensual para un año completo
- Retorna 12 meses con ingresos, egresos y balance de cada uno

---

### Rutas

**Blueprint:** `finanzas_bp` (prefijo: `/finanzas`)  
**Decoradores:** `@login_required` + `@duena_required`

#### `/finanzas/dashboard` (GET)
- Dashboard principal con tarjetas resumen (ingresos, egresos, balance)
- Gráficos de torta (Chart.js) para desglose por tipo y categoría
- Filtros: período (semana/mes/año/personalizado), paciente
- Tablas de desglose detallado

#### `/finanzas/gastos` (GET)
- Lista paginada de gastos con filtros
- Filtros: fecha_desde, fecha_hasta, categoria
- Total calculado al pie de tabla
- Badges de colores según categoría

#### `/finanzas/gastos/nuevo` (GET, POST)
- Formulario de creación de gasto
- Validación en servidor
- Mensajes flash de éxito/error
- Redirección a lista de gastos tras creación exitosa

#### `/finanzas/reportes` (GET)
- Reportes anuales con gráfico de barras + línea de balance
- Selector de año (últimos 5 años + próximos 2)
- Tabla mensual con totales anuales

#### `/finanzas/api/resumen` (GET - JSON)
- API endpoint para consultas AJAX
- Retorna resumen financiero en formato JSON
- Usado por gráficos dinámicos

---

### Templates

**`app/templates/finanzas/`**

#### `dashboard.html`
- Extends base.html
- Filtros en card colapsable
- 3 tarjetas de resumen con colores semánticos (verde=ingresos, rojo=egresos, azul/amarillo=balance)
- 2 gráficos de torta (Chart.js) lado a lado
- 2 tablas de desglose
- Botones de navegación a gastos y reportes
- JavaScript para toggle de fechas personalizadas

#### `gastos.html`
- Lista tabular con columnas: Fecha, Descripción, Categoría (badge), Monto, Observaciones, Creado por
- Filtros en card superior
- Footer con total calculado
- Link a nuevo_gasto.html
- Alert informativo si lista vacía

#### `nuevo_gasto.html`
- Formulario centrado (col-md-8 offset-md-2)
- Campos: descripcion (text), monto (number con step=0.01), fecha (date), categoria (select), observaciones (textarea)
- Fecha por defecto: hoy
- Tooltips explicativos para cada categoría
- Botones Cancelar (gris) y Guardar (azul)

#### `reportes.html`
- Selector de año en card
- Gráfico de barras combinado (ingresos verde, egresos rojo) + línea azul (balance)
- Tabla mensual con fila de totales anuales
- Colores dinámicos según balance positivo/negativo
- Formato de moneda en tooltips de Chart.js

---

## 🔐 Seguridad

### Control de Acceso
- **Decorador personalizado:** `@duena_required`
- **Verificación:** `current_user.tiene_acceso_finanzas()`
- **Roles permitidos:** Solo DUEÑA
- **Redirección:** Login si no autenticado, index si sin permisos
- **Mensajes:** Flash messages categorizados (warning, danger)

### Privacidad de Datos
- ❌ **No se registran en logs**: Montos, descripciones de gastos, datos de pacientes
- ✅ **Se registran en logs**: IDs numéricos, eventos técnicos, errores genéricos
- **Auditoría:** Cada gasto registra `creado_por_id` para trazabilidad

---

## 📐 Integración con Módulos Existentes

### Prestaciones (Ingresos)
- El módulo de finanzas **lee** datos de `Prestacion.monto_total` para calcular ingresos
- No modifica prestaciones, solo consulta
- Filtrado por `paciente_id` permite análisis por paciente individual

### Usuarios
- Relación FK en `Gasto.creado_por_id`
- Uso de `current_user.id` al crear gastos
- Display de `usuario.nombre_completo` en listas

### Navegación
- Link "Finanzas" en navbar cuando `current_user.tiene_acceso_finanzas() == True`
- Visible solo para DUEÑA, oculto para ODONTOLOGA y ADMIN
- Posición: Entre "Prácticas" y "Admin"

---

## 🎨 UI/UX

### Diseño Visual
- **Framework:** Bootstrap 5.1.3
- **Iconografía:** Font Awesome 6.0.0
- **Gráficos:** Chart.js (CDN)
- **Paleta de colores:**
  - Ingresos: `#198754` (verde Bootstrap success)
  - Egresos: `#dc3545` (rojo Bootstrap danger)
  - Balance positivo: `#0d6efd` (azul Bootstrap primary)
  - Balance negativo: `#ffc107` (amarillo Bootstrap warning)

### Componentes Interactivos
- **Filtros:** Auto-submit en selects, datepickers HTML5
- **Gráficos:** Tooltips con formato de moneda, leyenda en posición bottom
- **Tablas:** Hover effect, totales en footer con `table-active`
- **Badges:** Colores distintos para cada categoría de gasto

### Responsividad
- Grid responsivo (col-md-* breakpoints)
- Tablas con `table-responsive` wrapper
- Navbar colapsable en móviles
- Formularios en 2 columnas (monto/fecha) en desktop, 1 en móvil

---

## 🔧 Uso

### Flujo Típico de Uso

1. **Login como DUEÑA** (florencia / flor123)
2. **Acceder a Dashboard Financiero** → Clic en "Finanzas" en navbar
3. **Ver resumen del mes actual** (período por defecto)
4. **Registrar un gasto:**
   - Clic en "Gestionar Gastos"
   - Clic en "Nuevo Gasto"
   - Completar formulario (ej: "Compra de resinas composite" / $15000 / MATERIAL)
   - Guardar
5. **Analizar evolución anual:**
   - Clic en "Ver Reportes Anuales"
   - Seleccionar año
   - Ver gráfico mensual y tabla
6. **Filtrar por paciente:**
   - Volver a Dashboard
   - Seleccionar paciente en filtro
   - Ver ingresos específicos de ese paciente vs gastos totales

---

## 📊 Ejemplos de Datos

### Gasto de Ejemplo
```python
{
    "descripcion": "Resinas composite 3M ESPE",
    "monto": 28500.50,
    "fecha": "2025-01-15",
    "categoria": "MATERIAL",
    "observaciones": "Colores A2, A3, B1",
    "comprobante": None,
    "creado_por_id": 1  # Florencia López
}
```

### Resumen Financiero de Ejemplo
```python
{
    "ingresos": 125000.00,   # De prestaciones
    "egresos": 42500.00,     # De gastos
    "balance": 82500.00,     # Positivo
    "fecha_desde": "2025-01-01",
    "fecha_hasta": "2025-01-31"
}
```

---

## 🚀 Próximas Mejoras (Roadmap)

### Fase Futura (no implementado aún)
- [ ] Exportación a PDF/Excel de reportes
- [ ] Upload de comprobantes (archivos adjuntos)
- [ ] Presupuesto mensual con alertas de sobregasto
- [ ] Proyecciones financieras (forecast)
- [ ] Gráficos de línea para tendencias históricas
- [ ] Comparación interanual (2024 vs 2025)
- [ ] Integración con AFIP para exportación contable
- [ ] Dashboard móvil optimizado

---

## 🐛 Troubleshooting

### Problema: No veo el link "Finanzas" en navbar
- **Verificar:** `current_user.tiene_acceso_finanzas()` retorna True
- **Solución:** Solo el rol DUEÑA tiene acceso, verificar rol en Admin → Usuarios

### Problema: Error al crear gasto
- **Error común:** "Categoría inválida"
- **Solución:** Usar exactamente una de las 6 categorías (mayúsculas): MATERIAL, INSUMO, MATRICULA, CURSO, OPERATIVO, OTRO

### Problema: Balance no coincide
- **Verificar:** Fechas de prestaciones vs fechas de gastos
- **Causa común:** Gastos registrados con fecha futura o muy antigua
- **Solución:** Revisar filtros de fecha en ambas tablas

### Problema: Gráficos no se muestran
- **Verificar:** Consola del navegador (F12)
- **Causa común:** CDN de Chart.js bloqueado
- **Solución:** Verificar conexión a internet, revisar script tags en base.html

---

## 📝 Notas de Desarrollo

### Decisiones Técnicas

1. **¿Por qué Decimal para montos?**
   - Evita errores de redondeo con float
   - Precisión crítica para cálculos financieros
   - SQLite soporta NUMERIC para Decimal de Python

2. **¿Por qué Chart.js y no otra librería?**
   - Liviano (50KB minificado)
   - No requiere jQuery
   - Responsive por defecto
   - Documentación excelente

3. **¿Por qué no soft-delete en Gastos?**
   - Decisión: Hard delete (por ahora)
   - Razón: Simplificar MVP, agregar auditoría en fase futura
   - Mitigación: Logs de aplicación registran deletes

4. **¿Por qué servicios separados (crear/listar/estadísticas)?**
   - Seguir patrón SRP (Single Responsibility Principle)
   - Facilita testing unitario
   - Evita clases monolíticas
   - Consistencia con resto de servicios (paciente, turno, etc.)

---

## ✅ Checklist de Implementación

- [x] Modelo Gasto creado
- [x] Modelo agregado a `models/__init__.py`
- [x] Servicios de creación, listado y estadísticas
- [x] Blueprint finanzas_bp registrado
- [x] Decorador @duena_required implementado
- [x] Templates HTML con Bootstrap/Chart.js
- [x] Link en navbar con condicional de rol
- [x] Font Awesome agregado a base.html
- [x] Tabla gastos creada en DB (automático con db.create_all())
- [x] Documentación técnica (este archivo)

---

## 📚 Referencias

- **Chart.js Docs:** https://www.chartjs.org/docs/latest/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.1/
- **SQLAlchemy Decimal:** https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.Numeric
- **Flask-Login:** https://flask-login.readthedocs.io/
- **Font Awesome:** https://fontawesome.com/v6/icons

---

**Última actualización:** Diciembre 2025  
**Autor:** Sistema de desarrollo OdontoApp  
**Versión:** 1.0.0
