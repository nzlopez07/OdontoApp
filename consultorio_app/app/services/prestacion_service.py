from datetime import datetime
from app.database import db
from app.models import Prestacion, Paciente, Codigo, Practica, PrestacionPractica


class PrestacionService:
    @staticmethod
    def listar_prestaciones():
        return Prestacion.query.order_by(Prestacion.fecha.desc()).all()

    @staticmethod
    def listar_prestaciones_por_paciente(paciente_id: int):
        return (
            Prestacion.query.filter_by(paciente_id=paciente_id)
            .order_by(Prestacion.fecha.desc())
            .all()
        )

    @staticmethod
    def listar_prestaciones_por_paciente_pagina(paciente_id: int, pagina: int = 1, por_pagina: int = 10, filtros: dict = None):
        """Retorna prestaciones paginadas para un paciente con filtros opcionales.
        
        Args:
            paciente_id: ID del paciente
            pagina: Número de página (1-indexed)
            por_pagina: Elementos por página
            filtros: Dict con 'descripcion', 'monto_min', 'monto_max', 'fecha_desde', 'fecha_hasta'
            
        Returns:
            Dict con 'items', 'total', 'pagina_actual', 'total_paginas'
        """
        query = Prestacion.query.filter_by(paciente_id=paciente_id)
        
        # Aplicar filtros si existen
        if filtros:
            if filtros.get('descripcion'):
                query = query.filter(Prestacion.descripcion.ilike(f"%{filtros['descripcion']}%"))
            if filtros.get('monto_min'):
                try:
                    monto_min = float(filtros['monto_min'])
                    query = query.filter(Prestacion.monto >= monto_min)
                except (ValueError, TypeError):
                    pass
            if filtros.get('monto_max'):
                try:
                    monto_max = float(filtros['monto_max'])
                    query = query.filter(Prestacion.monto <= monto_max)
                except (ValueError, TypeError):
                    pass
        
        query = query.order_by(Prestacion.fecha.desc())
        total = query.count()
        total_paginas = (total + por_pagina - 1) // por_pagina if total > 0 else 1
        pagina_actual = max(1, min(pagina, total_paginas))
        offset = (pagina_actual - 1) * por_pagina
        items = query.offset(offset).limit(por_pagina).all()
        
        return {
            'items': items,
            'total': total,
            'pagina_actual': pagina_actual,
            'total_paginas': total_paginas,
            'por_pagina': por_pagina
        }

    @staticmethod
    def crear_prestacion(data: dict):
        try:
            practicas = data.get('practicas') or []
            subtotal = 0.0
            for item in practicas:
                practica = Practica.query.get(item['practica_id'])
                if practica:
                    subtotal += practica.monto_unitario * item.get('cantidad', 1)

            descuento_porcentaje = max(0.0, float(data.get('descuento_porcentaje') or 0))
            descuento_fijo = max(0.0, float(data.get('descuento_fijo') or 0))
            descuento_monto_porcentaje = subtotal * (descuento_porcentaje / 100)
            monto_total = subtotal - descuento_monto_porcentaje - descuento_fijo
            if monto_total < 0:
                monto_total = 0.0
            
            prestacion = Prestacion(
                paciente_id=int(data.get('paciente_id')),
                descripcion=data.get('descripcion'),
                monto=monto_total,
                fecha=datetime.now(),
                observaciones=data.get('observaciones'),
            )
            db.session.add(prestacion)
            db.session.flush()
            
            if not prestacion.id:
                raise ValueError("Prestación no tiene ID asignado después de flush")

            for item in practicas:
                practica = Practica.query.get(item['practica_id'])
                pp = PrestacionPractica(
                    prestacion_id=prestacion.id,
                    practica_id=item['practica_id'],
                    cantidad=item.get('cantidad', 1),
                    monto_unitario=practica.monto_unitario if practica else 0.0,
                    observaciones=item.get('observaciones')
                )
                db.session.add(pp)

            db.session.commit()
            return prestacion
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def listar_pacientes():
        return Paciente.query.all()

    @staticmethod
    def listar_codigos():
        return Codigo.query.all()

    @staticmethod
    def listar_practicas_para_paciente(paciente_id: int):
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return []
        practicas_os = []
        if paciente.obra_social_id:
            practicas_os = Practica.query.filter_by(proveedor_tipo='OBRA_SOCIAL', obra_social_id=paciente.obra_social_id).all()
        practicas_particular = Practica.query.filter_by(proveedor_tipo='PARTICULAR').all()
        return practicas_os + practicas_particular
