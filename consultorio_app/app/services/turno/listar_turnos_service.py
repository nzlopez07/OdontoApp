"""
Servicio para listar, buscar y paginar turnos con múltiples opciones.

Replica la funcionalidad de listar_turnos_paciente_pagina() y otros
métodos de listado del viejo turno_service.py.
"""

from datetime import date, datetime
from typing import Dict, List, Any, Tuple, Optional
from app.database.session import DatabaseSession
from app.models import Turno, Paciente, Estado
from sqlalchemy.orm import joinedload


class ListarTurnosService:
    """Servicio para listar y paginar turnos con búsqueda."""
    
    @staticmethod
    def obtener_turnos_hoy_filtrados(estados_permitidos: Optional[List[str]] = None, limite: int = 10):
        """
        Retorna objetos Turno para la fecha de hoy filtrando por estados permitidos.

        Respeta la migración gradual: si `estado_id` es NULL usa el campo legacy `estado`.
        Si `estado_id` no es NULL, filtra por `Estado.nombre`.

        Args:
            estados_permitidos: Lista de nombres de estado permitidos, ej: ["Pendiente", "Confirmado"].
            limite: Máximo de registros a retornar.

        Returns:
            Lista de modelos `Turno` ordenados por hora ascendente.
        """
        from sqlalchemy import or_, and_
        session = DatabaseSession.get_instance().session

        estados_permitidos = estados_permitidos or ["Pendiente", "Confirmado"]

        # Obtener IDs de estados permitidos (lista explícita para evitar SAWarning)
        estados_ids = [row.id for row in session.query(Estado).filter(Estado.nombre.in_(estados_permitidos)).all()]

        filtros = [Turno.fecha == date.today()]

        filtros.append(
            or_(
                # Caso legacy: estado_id NULL y estado string dentro de permitidos
                and_(Turno.estado_id.is_(None), Turno.estado.in_(estados_permitidos)),
                # Caso nuevo: estado_id en estados permitidos
                Turno.estado_id.in_(estados_ids)
            )
        )

        turnos = (
            session.query(Turno)
            .options(joinedload(Turno.paciente), joinedload(Turno.estado_obj))
            .filter(*filtros)
            .order_by(Turno.hora)
            .limit(limite)
            .all()
        )

        return turnos

    def listar_turnos_paciente_pagina(
        paciente_id: int,
        pagina: int = 1,
        por_pagina: int = 10,
        filtro_estado: Optional[str] = None,
        filtro_fecha_desde: Optional[date] = None,
        filtro_fecha_hasta: Optional[date] = None,
        incluir_pasados: bool = True,
    ) -> Dict[str, Any]:
        """
        Lista los turnos de un paciente de forma paginada con filtros opcionales.
        
        Args:
            paciente_id: ID del paciente
            pagina: Número de página (1-indexed)
            por_pagina: Cantidad de registros por página
            filtro_estado: Filtrar por estado específico (ej: "Confirmado", "Atendido")
            filtro_fecha_desde: Filtrar desde esta fecha (inclusive)
            filtro_fecha_hasta: Filtrar hasta esta fecha (inclusive)
            incluir_pasados: Si True, incluye turnos de fechas pasadas
            
        Returns:
            Dict con estructura:
            {
                'total': int,
                'pagina': int,
                'por_pagina': int,
                'paginas_totales': int,
                'turnos': [
                    {
                        'id': int,
                        'fecha': date,
                        'hora': time,
                        'duracion': int,
                        'detalle': str,
                        'estado': str,
                        'creado_en': datetime,
                    }
                ]
            }
        """
        session = DatabaseSession.get_instance().session
        
        # Validar página
        pagina = max(1, pagina)
        por_pagina = max(1, min(por_pagina, 100))  # Max 100 por página
        
        # Construir query base
        query = session.query(Turno).filter(Turno.paciente_id == paciente_id)
        
        # Aplicar filtro de fecha de inicio (no pasados por defecto)
        if not incluir_pasados:
            query = query.filter(Turno.fecha >= date.today())
        
        # Aplicar filtro de rango de fechas
        if filtro_fecha_desde:
            query = query.filter(Turno.fecha >= filtro_fecha_desde)
        if filtro_fecha_hasta:
            query = query.filter(Turno.fecha <= filtro_fecha_hasta)
        
        # Aplicar filtro de estado
        if filtro_estado:
            estado_obj = Estado.query.filter_by(nombre=filtro_estado).first()
            if estado_obj:
                query = query.filter(Turno.estado_id == estado_obj.id)
            else:
                # Estado inexistente -> sin resultados
                query = query.filter(False)
        
        # Contar total antes de paginar
        total = query.count()
        
        # Paginar
        offset = (pagina - 1) * por_pagina
        turnos = query.order_by(
            Turno.fecha.desc(),
            Turno.hora.desc()
        ).offset(offset).limit(por_pagina).all()
        
        # Calcular páginas totales
        import math
        paginas_totales = math.ceil(total / por_pagina) if total > 0 else 1
        
        # Serializar turnos
        turnos_dict = [
            {
                'id': t.id,
                'fecha': t.fecha,
                'hora': t.hora,
                'duracion': t.duracion,
                'detalle': t.detalle,
                'estado': t.estado_nombre,
                'creado_en': t.creado_en,
            }
            for t in turnos
        ]
        
        return {
            'total': total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'paginas_totales': paginas_totales,
            'turnos': turnos_dict,
        }
    
    @staticmethod
    def obtener_turnos_por_fecha(fecha: date) -> List[Dict[str, Any]]:
        """
        Obtiene todos los turnos de una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            
        Returns:
            Lista de turnos ordenados por hora
        """
        session = DatabaseSession.get_instance().session
        
        turnos = session.query(Turno).options(
            joinedload(Turno.paciente)
        ).filter(
            Turno.fecha == fecha
        ).order_by(Turno.hora).all()
        
        return [
            {
                'id': t.id,
                'paciente': {
                    'id': t.paciente.id,
                    'nombre': t.paciente.nombre,
                    'apellido': t.paciente.apellido,
                    'dni': t.paciente.dni,
                },
                'fecha': t.fecha,
                'hora': t.hora,
                'duracion': t.duracion,
                'detalle': t.detalle,
                'estado': t.estado_nombre,
            }
            for t in turnos
        ]
    
    @staticmethod
    def obtener_turnos_por_paciente(paciente_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los turnos de un paciente.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Lista de turnos ordenados por fecha descendente
        """
        session = DatabaseSession.get_instance().session
        
        turnos = session.query(Turno).filter(
            Turno.paciente_id == paciente_id
        ).order_by(
            Turno.fecha.desc(),
            Turno.hora.desc()
        ).all()
        
        return [
            {
                'id': t.id,
                'fecha': t.fecha,
                'hora': t.hora,
                'duracion': t.duracion,
                'detalle': t.detalle,
                'estado': t.estado_nombre,
            }
            for t in turnos
        ]
    
    @staticmethod
    def obtener_turnos_proximos(limite: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los próximos turnos desde hoy.
        
        Args:
            limite: Número máximo de turnos a retornar
            
        Returns:
            Lista de próximos turnos
        """
        session = DatabaseSession.get_instance().session
        
        turnos = session.query(Turno).options(
            joinedload(Turno.paciente)
        ).filter(
            Turno.fecha >= date.today()
        ).order_by(
            Turno.fecha,
            Turno.hora
        ).limit(limite).all()
        
        return [
            {
                'id': t.id,
                'paciente': {
                    'id': t.paciente.id,
                    'nombre': t.paciente.nombre,
                    'apellido': t.paciente.apellido,
                },
                'fecha': t.fecha,
                'hora': t.hora,
                'duracion': t.duracion,
                'estado': t.estado_nombre,
            }
            for t in turnos
        ]
    
    @staticmethod
    def listar_y_actualizar_no_atendidos() -> Dict[str, int]:
        """
        Lista todos los turnos y actualiza automáticamente los que han vencido.
        
        Marca como 'NoAtendido' aquellos turnos cuya fecha/hora ya pasó y están
        en un estado diferente a 'Atendido', 'NoAtendido' o 'Cancelado'.
        
        Returns:
            Dict con estadísticas:
            {
                'turnos_actualizados': int,
                'total_turnos': int,
            }
        """
        session = DatabaseSession.get_instance().session
        
        ahora = datetime.now()
        hoy = date.today()
        
        # Query todos los turnos que potencialmente podrían ser vencidos
        estados = {
            e.nombre: e.id for e in session.query(Estado).filter(Estado.nombre.in_([
                'Atendido', 'NoAtendido', 'Cancelado'
            ])).all()
        }

        if 'NoAtendido' not in estados:
            return {'turnos_actualizados': 0, 'total_turnos': session.query(Turno).count()}

        filtros = [Turno.estado_id.is_(None)]
        ids_excluir = [eid for name, eid in estados.items() if name in ['Atendido', 'NoAtendido', 'Cancelado']]
        if ids_excluir:
            filtros.append(~Turno.estado_id.in_(ids_excluir))

        turnos = session.query(Turno).filter(*filtros).all()
        
        cambios = 0
        for turno in turnos:
            es_vencido = False
            
            # Caso 1: Fecha en el pasado
            if turno.fecha < hoy:
                es_vencido = True
            # Caso 2: Fecha hoy pero hora pasó
            elif turno.fecha == hoy and turno.hora:
                turno_dt = datetime.combine(turno.fecha, turno.hora)
                if turno_dt < ahora:
                    es_vencido = True
            
            # Marcar como NoAtendido si vencido
            if es_vencido:
                turno.estado_id = estados.get('NoAtendido')
                turno.estado = 'NoAtendido'
                cambios += 1
        
        # Commit batch update
        if cambios > 0:
            session.commit()
        
        total_turnos = session.query(Turno).count()
        
        return {
            'turnos_actualizados': cambios,
            'total_turnos': total_turnos,
        }
