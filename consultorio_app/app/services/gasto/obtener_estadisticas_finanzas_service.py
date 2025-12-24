"""
Servicio para obtener estadísticas financieras.
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func, and_, or_

from app.database import db
from app.models import (
    Gasto,
    ObraSocial,
    Paciente,
    Practica,
    Prestacion,
    PrestacionPractica,
)


class ObtenerEstadisticasFinanzasService:
    """Servicio para obtener estadísticas financieras."""
    
    @staticmethod
    def obtener_resumen(
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        paciente_id: Optional[int] = None
    ) -> Dict:
        """
        Obtiene resumen financiero con ingresos, egresos y balance.
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            paciente_id: ID del paciente para filtrar ingresos (opcional)
            
        Returns:
            Diccionario con resumen financiero
        """
        # Calcular ingresos (de Prestaciones)
        query_ingresos = db.session.query(
            func.sum(Prestacion.monto).label('total')
        )
        
        filtros_ingresos = []
        if fecha_desde:
            filtros_ingresos.append(func.date(Prestacion.fecha) >= fecha_desde)
        if fecha_hasta:
            filtros_ingresos.append(func.date(Prestacion.fecha) <= fecha_hasta)
        if paciente_id:
            filtros_ingresos.append(Prestacion.paciente_id == paciente_id)
        
        if filtros_ingresos:
            query_ingresos = query_ingresos.filter(and_(*filtros_ingresos))
        
        total_ingresos = query_ingresos.scalar() or Decimal('0')
        
        # Calcular egresos (de Gastos)
        query_egresos = db.session.query(
            func.sum(Gasto.monto).label('total')
        )
        
        filtros_egresos = []
        if fecha_desde:
            filtros_egresos.append(Gasto.fecha >= fecha_desde)
        if fecha_hasta:
            filtros_egresos.append(Gasto.fecha <= fecha_hasta)
        
        if filtros_egresos:
            query_egresos = query_egresos.filter(and_(*filtros_egresos))
        
        total_egresos = query_egresos.scalar() or Decimal('0')
        
        # Calcular balance
        # Asegurar tipos Decimal para evitar mezclas float/Decimal
        total_ingresos = Decimal(total_ingresos)
        total_egresos = Decimal(total_egresos)
        balance = total_ingresos - total_egresos
        
        return {
            'ingresos': float(total_ingresos),
            'egresos': float(total_egresos),
            'balance': float(balance),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        }
    
    @staticmethod
    def obtener_ingresos_por_tipo(
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene ingresos agrupados por Obra Social (fuente de pago).
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            Lista de diccionarios con fuente y total
        """
        query = db.session.query(
            func.coalesce(ObraSocial.nombre, 'Particular').label('fuente'),
            func.sum(Prestacion.monto).label('total'),
            func.count(Prestacion.id).label('cantidad')
        ).join(Paciente, Prestacion.paciente_id == Paciente.id)
        query = query.outerjoin(ObraSocial, Paciente.obra_social_id == ObraSocial.id)
        query = query.group_by('fuente')
        
        filtros = []
        if fecha_desde:
            filtros.append(func.date(Prestacion.fecha) >= fecha_desde)
        if fecha_hasta:
            filtros.append(func.date(Prestacion.fecha) <= fecha_hasta)
        
        if filtros:
            query = query.filter(and_(*filtros))
        
        resultados = query.all()
        
        return [
            {
                'fuente': fuente,
                'total': float(total),
                'cantidad': cantidad
            }
            for fuente, total, cantidad in resultados
        ]

    @staticmethod
    def obtener_ingresos_por_practica(
        obra_social: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene ingresos agrupados por práctica (código + descripción) para una obra social.

        Distribuye el monto de cada prestación proporcionalmente por cantidad de prácticas
        asociadas para no desbalancear el total de ingresos.

        Args:
            obra_social: Nombre de la obra social ("Particular" considera pacientes sin obra social)
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)

        Returns:
            Lista de diccionarios con código, descripción, cantidad y total
        """
        session = db.session

        total_practicas_window = func.sum(PrestacionPractica.cantidad).over(
            partition_by=Prestacion.id
        ).label('total_practicas')

        query = session.query(
            Prestacion.id.label('prestacion_id'),
            Prestacion.monto.label('monto_prestacion'),
            PrestacionPractica.cantidad.label('cantidad_practica'),
            total_practicas_window,
            Practica.codigo.label('codigo'),
            Practica.descripcion.label('descripcion')
        ).join(Paciente, Prestacion.paciente_id == Paciente.id)
        query = query.outerjoin(ObraSocial, Paciente.obra_social_id == ObraSocial.id)
        query = query.join(PrestacionPractica, PrestacionPractica.prestacion_id == Prestacion.id)
        query = query.join(Practica, PrestacionPractica.practica_id == Practica.id)

        filtros = []
        if fecha_desde:
            filtros.append(func.date(Prestacion.fecha) >= fecha_desde)
        if fecha_hasta:
            filtros.append(func.date(Prestacion.fecha) <= fecha_hasta)

        if obra_social and obra_social.lower() not in ('todas', 'todo'):
            if obra_social.lower() == 'particular':
                filtros.append(or_(ObraSocial.nombre == 'Particular', ObraSocial.id.is_(None)))
            else:
                filtros.append(func.lower(ObraSocial.nombre) == obra_social.lower())

        if filtros:
            query = query.filter(and_(*filtros))

        resultados = query.all()

        acumulado: Dict[str, Dict[str, float]] = {}
        for row in resultados:
            total_practicas = row.total_practicas or 0
            cantidad_practica = row.cantidad_practica or 0
            if total_practicas == 0:
                monto_practica = 0
            else:
                monto_practica = (row.monto_prestacion or 0) * (cantidad_practica / total_practicas)

            codigo = row.codigo or 'Sin código'
            descripcion = row.descripcion or 'Sin descripción'
            etiqueta = f"{codigo} - {descripcion}"

            if etiqueta not in acumulado:
                acumulado[etiqueta] = {
                    'codigo': codigo,
                    'descripcion': descripcion,
                    'cantidad': 0,
                    'total': 0.0,
                }

            acumulado[etiqueta]['cantidad'] += cantidad_practica
            acumulado[etiqueta]['total'] += float(monto_practica)

        # Ordenar por total desc para una lectura rápida
        return sorted(
            acumulado.values(),
            key=lambda x: x['total'],
            reverse=True
        )
    
    @staticmethod
    def obtener_egresos_por_categoria(
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene egresos agrupados por categoría.
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            Lista de diccionarios con categoría y total
        """
        query = db.session.query(
            Gasto.categoria,
            func.sum(Gasto.monto).label('total'),
            func.count(Gasto.id).label('cantidad')
        ).group_by(Gasto.categoria)
        
        filtros = []
        if fecha_desde:
            filtros.append(Gasto.fecha >= fecha_desde)
        if fecha_hasta:
            filtros.append(Gasto.fecha <= fecha_hasta)
        
        if filtros:
            query = query.filter(and_(*filtros))
        
        resultados = query.all()
        
        return [
            {
                'categoria': categoria,
                'total': float(total),
                'cantidad': cantidad
            }
            for categoria, total, cantidad in resultados
        ]
    
    @staticmethod
    def obtener_evolucion_mensual(anio: int) -> Dict:
        """
        Obtiene evolución de ingresos y egresos por mes.
        
        Args:
            anio: Año para el reporte
            
        Returns:
            Diccionario con datos mensuales
        """
        # Nombres de meses en español
        nombres_meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        meses_data = []
        
        for mes in range(1, 13):
            # Primer y último día del mes
            if mes == 12:
                fecha_desde = date(anio, mes, 1)
                fecha_hasta = date(anio + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_desde = date(anio, mes, 1)
                fecha_hasta = date(anio, mes + 1, 1) - timedelta(days=1)
            
            # Obtener resumen del mes
            resumen = ObtenerEstadisticasFinanzasService.obtener_resumen(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            meses_data.append({
                'mes': mes,
                'nombre': nombres_meses[mes - 1],
                'ingresos': resumen['ingresos'],
                'egresos': resumen['egresos'],
                'balance': resumen['balance']
            })
        
        return {
            'anio': anio,
            'meses': meses_data
        }
