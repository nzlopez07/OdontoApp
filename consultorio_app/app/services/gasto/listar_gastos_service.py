"""
Servicio para listar y filtrar gastos.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import and_

from app.database import db
from app.models import Gasto


class ListarGastosService:
    """Servicio para listar y filtrar gastos."""
    
    @staticmethod
    def listar(
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        categoria: Optional[str] = None
    ) -> List[Gasto]:
        """
        Lista gastos con filtros opcionales.
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            categoria: Categoría (opcional)
            
        Returns:
            Lista de gastos
        """
        query = Gasto.query
        
        # Aplicar filtros
        filtros = []
        
        if fecha_desde:
            filtros.append(Gasto.fecha >= fecha_desde)
        
        if fecha_hasta:
            filtros.append(Gasto.fecha <= fecha_hasta)
        
        if categoria:
            filtros.append(Gasto.categoria == categoria)
        
        if filtros:
            query = query.filter(and_(*filtros))
        
        # Ordenar por fecha descendente
        query = query.order_by(Gasto.fecha.desc(), Gasto.fecha_creacion.desc())
        
        return query.all()
    
    @staticmethod
    def obtener_por_id(gasto_id: int) -> Optional[Gasto]:
        """
        Obtiene un gasto por ID.
        
        Args:
            gasto_id: ID del gasto
            
        Returns:
            Gasto o None si no existe
        """
        return db.session.get(Gasto, gasto_id)
