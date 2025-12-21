"""
Servicios para la gestión de turnos del consultorio odontológico.

Este módulo contiene la lógica de negocio para:
- Crear y gestionar turnos
- Validar disponibilidad de horarios
- Gestionar estados de turnos
- Notificaciones y recordatorios
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from app.database.session import DatabaseSession
from app.models import Turno, Paciente, Estado, CambioEstado


class TurnoService:
    """Servicio para la gestión de turnos."""
    
    # Configuración de horarios de trabajo
    HORARIO_INICIO = time(8, 0)  # 8:00 AM
    HORARIO_FIN = time(21, 0)    # 9:00 PM
    DURACION_TURNO = 60          # Grid base visual de 60 minutos (slots de 1h)
    DIAS_LABORABLES = [0, 1, 2, 3, 4, 5]  # Lunes a Sábado (0=Lunes, 6=Domingo)
    
    # Matriz de transiciones de estado válidas
    # Formato: estado_actual -> [estados_permitidos]
    TRANSICIONES_VALIDAS = {
        'Pendiente': ['Confirmado', 'Cancelado', 'NoAtendido'],
        'Confirmado': ['Atendido', 'NoAtendido', 'Cancelado'],
        'Atendido': [],  # Estado final, no se puede cambiar
        'NoAtendido': [],  # Estado final, no se puede cambiar
        'Cancelado': []  # Estado final, no se puede cambiar
    }
    
    @staticmethod
    def obtener_semana_agenda(fecha_inicio = None) -> Dict[str, Any]:
        """Obtiene los turnos de una semana para visualizar en agenda.
        
        Args:
            fecha_inicio: Primera fecha de la semana (lunes). Puede ser date, datetime o string YYYY-MM-DD.
                         Si no se proporciona, usa la semana actual.
            
        Returns:
            Dict con estructura de días y horas para la agenda.
        """
        # Convertir string a date si es necesario
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        elif isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()
        
        if not fecha_inicio:
            hoy = date.today()
            dias_atras = hoy.weekday()  # 0=Lunes, 6=Domingo
            fecha_inicio = hoy - timedelta(days=dias_atras)
        
        # Construir semana (lunes a sábado)
        semana = {}
        dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        
        for i in range(6):  # Lunes a Sábado
            fecha_dia = fecha_inicio + timedelta(days=i)
            dia_nombre = dias_nombres[i]
            
            semana[dia_nombre] = {
                'fecha': fecha_dia,
                'turnos': [],            # lista de Turno
                'bloques': []            # lista de dicts con posiciones precomputadas para la UI
            }
        
        # Obtener turnos de la semana
        fecha_fin = fecha_inicio + timedelta(days=6)
        turnos = Turno.query.filter(
            and_(
                Turno.fecha >= fecha_inicio,
                Turno.fecha <= fecha_fin
            )
        ).all()
        
        print(f"[DEBUG] Buscando turnos entre {fecha_inicio} y {fecha_fin}")
        print(f"[DEBUG] Turnos encontrados: {len(turnos)}")
        
        total_minutos_dia = (datetime.combine(date.today(), TurnoService.HORARIO_FIN) -
                              datetime.combine(date.today(), TurnoService.HORARIO_INICIO)).seconds // 60
        hora_inicio_min = TurnoService.HORARIO_INICIO.hour * 60 + TurnoService.HORARIO_INICIO.minute
        
        # Distribuir turnos en la agenda por día y precomputar posiciones (top/height en %)
        for turno in turnos:
            print(f"[DEBUG] Turno: {turno.id} - Fecha: {turno.fecha} - Hora: {turno.hora} - Paciente: {turno.paciente}")
            if not turno.hora:
                print(f"[DEBUG] Turno {turno.id} sin hora, saltando")
                continue
            
            dia_semana = turno.fecha.weekday()  # 0=Lunes
            if dia_semana < 6:  # Solo lunes a sábado
                dia_nombre = dias_nombres[dia_semana]
                semana[dia_nombre]['turnos'].append(turno)
                
                # Calcular posición relativa
                inicio_min = turno.hora.hour * 60 + turno.hora.minute
                offset_min = inicio_min - hora_inicio_min
                if offset_min < 0:
                    # comienza antes del inicio de jornada, recortar
                    turno_duracion = getattr(turno, 'duracion', 30) + offset_min  # resta
                    offset_min = 0
                else:
                    turno_duracion = getattr(turno, 'duracion', 30)
                
                # Recortar si excede el fin de jornada
                if offset_min > total_minutos_dia:
                    # fuera del horario visible
                    print(f"[DEBUG] Turno {turno.id} inicia fuera del horario visible, saltando")
                    continue
                
                if offset_min + turno_duracion > total_minutos_dia:
                    turno_duracion = max(0, total_minutos_dia - offset_min)
                
                top_pct = (offset_min / total_minutos_dia) * 100.0
                height_pct = (max(5, turno_duracion) / total_minutos_dia) * 100.0  # asegurar mínimo visual
                
                semana[dia_nombre]['bloques'].append({
                    'turno': turno,
                    'top_pct': top_pct,
                    'height_pct': height_pct
                })
                print(f"[DEBUG] Turno {turno.id} pos -> top:{top_pct:.2f}% height:{height_pct:.2f}% en {dia_nombre}")
        
        # Generar marcadores horarios cada 1h
        horas_marcadores = []
        horas_labels = []
        actual = datetime.combine(date.today(), TurnoService.HORARIO_INICIO)
        fin = datetime.combine(date.today(), TurnoService.HORARIO_FIN)
        i = 0
        while actual <= fin:
            minutos_desde_inicio = (actual - datetime.combine(date.today(), TurnoService.HORARIO_INICIO)).seconds // 60
            horas_marcadores.append((minutos_desde_inicio / total_minutos_dia) * 100.0)
            horas_labels.append(actual.strftime('%H:00'))
            i += 1
            actual += timedelta(hours=1)
        
        return {
            'semana': semana,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_inicio + timedelta(days=5),
            'semana_siguiente': fecha_inicio + timedelta(days=7),
            'semana_anterior': fecha_inicio - timedelta(days=7),
            'horas_marcadores': horas_marcadores,
            'horas_labels': horas_labels,
            'total_minutos_dia': total_minutos_dia
        }
    
    @staticmethod
    def validar_transicion_estado(estado_actual: str, estado_nuevo: str) -> tuple:
        """Valida si una transición de estado es válida.
        
        Args:
            estado_actual: Estado actual del turno
            estado_nuevo: Estado al que se quiere cambiar
            
        Returns:
            Tupla (es_valida, mensaje_error)
        """
        # Normalizar estados
        estado_actual = estado_actual or 'Pendiente'
        
        # Verificar que ambos estados sean válidos
        estados_validos = ['Pendiente', 'Confirmado', 'Atendido', 'NoAtendido', 'Cancelado']
        if estado_nuevo not in estados_validos:
            return False, f'Estado "{estado_nuevo}" no es válido. Estados válidos: {", ".join(estados_validos)}'
        
        # Si es el mismo estado, permitir (es un no-op)
        if estado_actual == estado_nuevo:
            return False, f'El turno ya tiene el estado "{estado_nuevo}"'
        
        # Verificar transición según matriz
        if estado_actual not in TurnoService.TRANSICIONES_VALIDAS:
            return False, f'Estado actual "{estado_actual}" no reconocido'
        
        transiciones_permitidas = TurnoService.TRANSICIONES_VALIDAS[estado_actual]
        if estado_nuevo not in transiciones_permitidas:
            if not transiciones_permitidas:
                return False, f'El turno está en estado "{estado_actual}" (final). No se pueden hacer cambios de estado.'
            return False, f'No se puede cambiar de "{estado_actual}" a "{estado_nuevo}". Transiciones permitidas: {", ".join(transiciones_permitidas)}'
        
        return True, None
    
    @staticmethod
    def verificar_solapamiento(fecha: date, hora_inicio: time, duracion: int, turno_id_excluir: int = None) -> tuple:
        """Verifica si un turno se solapa con otros turnos existentes.
        
        Args:
            fecha: Fecha del turno a verificar
            hora_inicio: Hora de inicio del turno
            duracion: Duración en minutos del turno
            turno_id_excluir: ID de turno a excluir de la verificación (para ediciones)
            
        Returns:
            Tupla (hay_solapamiento, mensaje_error, lista_turnos_solapados)
        """
        # Convertir hora a minutos desde medianoche para cálculos
        inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
        fin_min = inicio_min + duracion
        
        # Obtener todos los turnos del mismo día (excepto el que estamos editando)
        query = Turno.query.filter(Turno.fecha == fecha)
        if turno_id_excluir:
            query = query.filter(Turno.id != turno_id_excluir)
        
        turnos_dia = query.all()
        
        turnos_solapados = []
        for turno_existente in turnos_dia:
            if not turno_existente.hora:
                continue
            
            # Calcular rango del turno existente
            turno_inicio_min = turno_existente.hora.hour * 60 + turno_existente.hora.minute
            turno_duracion = getattr(turno_existente, 'duracion', 30)
            turno_fin_min = turno_inicio_min + turno_duracion
            
            # Verificar solapamiento: dos rangos se solapan si uno empieza antes de que termine el otro
            # [inicio1, fin1) solapa con [inicio2, fin2) si: inicio1 < fin2 AND inicio2 < fin1
            if inicio_min < turno_fin_min and turno_inicio_min < fin_min:
                turnos_solapados.append(turno_existente)
        
        if turnos_solapados:
            detalles = []
            for t in turnos_solapados:
                t_fin = datetime.combine(date.today(), t.hora) + timedelta(minutes=getattr(t, 'duracion', 30))
                detalles.append(
                    f"{t.hora.strftime('%H:%M')}-{t_fin.strftime('%H:%M')} ({t.paciente.nombre} {t.paciente.apellido})"
                )
            mensaje = f"El horario se solapa con {len(turnos_solapados)} turno(s) existente(s): {', '.join(detalles)}"
            return True, mensaje, turnos_solapados
        
        return False, None, []
    
    @staticmethod
    def crear_turno(paciente_id: int, fecha: date, hora: time, 
                   observaciones: str = None) -> Dict[str, Any]:
        """
        Crea un nuevo turno para un paciente.
        
        Args:
            paciente_id: ID del paciente
            fecha: Fecha del turno
            hora: Hora del turno
            observaciones: Observaciones adicionales
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Validar que el paciente existe
            paciente = Paciente.query.get(paciente_id)
            if not paciente:
                return {
                    'success': False,
                    'error': 'Paciente no encontrado',
                    'turno': None
                }
            
            # Validar disponibilidad
            disponible = TurnoService.verificar_disponibilidad(fecha, hora)
            if not disponible['disponible']:
                return {
                    'success': False,
                    'error': disponible['motivo'],
                    'turno': None
                }
            
            # Obtener estado inicial (Pendiente)
            estado_pendiente = Estado.query.filter_by(nombre='Pendiente').first()
            if not estado_pendiente:
                return {
                    'success': False,
                    'error': 'Estado "Pendiente" no encontrado en el sistema',
                    'turno': None
                }
            
            # Crear el turno
            turno = Turno(
                paciente_id=paciente_id,
                fecha=fecha,
                hora=hora,
                estado_id=estado_pendiente.id,
                observaciones=observaciones,
                fecha_creacion=datetime.now()
            )
            
            session = DatabaseSession.get_instance().session
            session.add(turno)
            session.flush()  # Para obtener el ID del turno
            
            # Registrar cambio de estado inicial
            cambio_estado = CambioEstado(
                turno_id=turno.id,
                estado_anterior_id=None,
                estado_nuevo_id=estado_pendiente.id,
                fecha_cambio=datetime.now(),
                motivo='Turno creado'
            )
            
            session.add(cambio_estado)
            session.commit()
            
            return {
                'success': True,
                'error': None,
                'turno': turno
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Error al crear turno: {str(e)}',
                'turno': None
            }
    
    @staticmethod
    def verificar_disponibilidad(fecha: date, hora: time) -> Dict[str, Any]:
        """
        Verifica si un horario está disponible para agendar un turno.
        
        Args:
            fecha: Fecha a verificar
            hora: Hora a verificar
            
        Returns:
            Dict con información de disponibilidad
        """
        # Verificar que la fecha no sea en el pasado
        if fecha < date.today():
            return {
                'disponible': False,
                'motivo': 'No se pueden agendar turnos en fechas pasadas'
            }
        
        # Verificar que sea día laborable
        if fecha.weekday() not in TurnoService.DIAS_LABORABLES:
            return {
                'disponible': False,
                'motivo': 'Los turnos solo se pueden agendar de lunes a viernes'
            }
        
        # Verificar horario de trabajo
        if hora < TurnoService.HORARIO_INICIO or hora >= TurnoService.HORARIO_FIN:
            return {
                'disponible': False,
                'motivo': f'Los turnos solo se pueden agendar entre {TurnoService.HORARIO_INICIO.strftime("%H:%M")} y {TurnoService.HORARIO_FIN.strftime("%H:%M")}'
            }
        
        # Verificar que no haya otro turno en el mismo horario
        turno_existente = Turno.query.filter(
            and_(
                Turno.fecha == fecha,
                Turno.hora == hora
            )
        ).first()
        
        if turno_existente:
            return {
                'disponible': False,
                'motivo': 'Ya existe un turno agendado para ese horario'
            }
        
        return {
            'disponible': True,
            'motivo': None
        }

    @staticmethod
    def listar_turnos_paciente(paciente_id: int):
        return (
            Turno.query.filter_by(paciente_id=paciente_id)
            .order_by(Turno.fecha.desc(), Turno.hora.desc())
            .all()
        )

    @staticmethod
    def listar_turnos_paciente_pagina(paciente_id: int, pagina: int = 1, por_pagina: int = 10):
        """Retorna turnos paginados para un paciente.
        
        Args:
            paciente_id: ID del paciente
            pagina: Número de página (1-indexed)
            por_pagina: Elementos por página
            
        Returns:
            Dict con 'items', 'total', 'pagina_actual', 'total_paginas'
        """
        query = Turno.query.filter_by(paciente_id=paciente_id).order_by(Turno.fecha.desc(), Turno.hora.desc())
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
    def obtener_horarios_disponibles(fecha: date) -> List[time]:
        """
        Obtiene la lista de horarios disponibles para una fecha específica.
        
        Args:
            fecha: Fecha para consultar disponibilidad
            
        Returns:
            Lista de horarios disponibles
        """
        # Verificar que sea día laborable
        if fecha.weekday() not in TurnoService.DIAS_LABORABLES:
            return []
        
        # Generar todos los horarios posibles
        horarios_posibles = []
        hora_actual = TurnoService.HORARIO_INICIO
        
        while hora_actual < TurnoService.HORARIO_FIN:
            horarios_posibles.append(hora_actual)
            # Agregar duración del turno
            dt = datetime.combine(date.today(), hora_actual)
            dt += timedelta(minutes=TurnoService.DURACION_TURNO)
            hora_actual = dt.time()
        
        # Obtener turnos ya agendados para esa fecha
        turnos_agendados = Turno.query.filter_by(fecha=fecha).all()
        horarios_ocupados = [turno.hora for turno in turnos_agendados]
        
        # Filtrar horarios disponibles
        horarios_disponibles = [
            hora for hora in horarios_posibles 
            if hora not in horarios_ocupados
        ]
        
        return horarios_disponibles
    
    @staticmethod
    def cambiar_estado_turno(turno_id: int, nuevo_estado_nombre: str, 
                           motivo: str = None) -> Dict[str, Any]:
        """
        Cambia el estado de un turno.
        
        Args:
            turno_id: ID del turno
            nuevo_estado_nombre: Nombre del nuevo estado
            motivo: Motivo del cambio
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Obtener el turno
            turno = Turno.query.get(turno_id)
            if not turno:
                return {
                    'success': False,
                    'error': 'Turno no encontrado'
                }
            
            # Obtener el nuevo estado
            nuevo_estado = Estado.query.filter_by(nombre=nuevo_estado_nombre).first()
            if not nuevo_estado:
                return {
                    'success': False,
                    'error': f'Estado "{nuevo_estado_nombre}" no encontrado'
                }
            
            # Verificar que no sea el mismo estado
            if turno.estado_id == nuevo_estado.id:
                return {
                    'success': False,
                    'error': 'El turno ya tiene ese estado'
                }
            
            # Guardar estado anterior
            estado_anterior_id = turno.estado_id
            
            # Cambiar estado
            turno.estado_id = nuevo_estado.id
            
            # Registrar cambio de estado
            cambio_estado = CambioEstado(
                turno_id=turno_id,
                estado_anterior_id=estado_anterior_id,
                estado_nuevo_id=nuevo_estado.id,
                fecha_cambio=datetime.now(),
                motivo=motivo or f'Cambio a {nuevo_estado_nombre}'
            )
            
            session = DatabaseSession.get_instance().session
            session.add(cambio_estado)
            session.commit()
            
            return {
                'success': True,
                'error': None,
                'turno': turno
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Error al cambiar estado: {str(e)}'
            }
    
    @staticmethod
    def obtener_turnos_por_fecha(fecha: date) -> List[Turno]:
        """
        Obtiene todos los turnos para una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            
        Returns:
            Lista de turnos
        """
        return Turno.query.filter_by(fecha=fecha).order_by(Turno.hora).all()
    
    @staticmethod
    def obtener_turnos_por_paciente(paciente_id: int) -> List[Turno]:
        """
        Obtiene todos los turnos de un paciente.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Lista de turnos
        """
        return Turno.query.filter_by(paciente_id=paciente_id).order_by(
            Turno.fecha.desc(), Turno.hora.desc()
        ).all()
    
    @staticmethod
    def obtener_turnos_proximos(limite: int = 10) -> List[Turno]:
        """
        Obtiene los próximos turnos.
        
        Args:
            limite: Número máximo de turnos a retornar
            
        Returns:
            Lista de próximos turnos
        """
        return Turno.query.filter(
            Turno.fecha >= date.today()
        ).order_by(Turno.fecha, Turno.hora).limit(limite).all()

    # === Métodos adaptados a la app actual (estado como string) ===
    @staticmethod
    def actualizar_no_atendidos(session):
        """Marca turnos vencidos como NoAtendido."""
        ahora = datetime.now()
        hoy = date.today()

        vencidos = (
            session.query(Turno)
            .filter(Turno.estado.is_(None) | ~Turno.estado.in_(['Atendido', 'NoAtendido', 'Cancelado']))
            .all()
        )

        cambios = 0
        for turno in vencidos:
            es_vencido = False
            if turno.fecha < hoy:
                es_vencido = True
            elif turno.fecha == hoy and turno.hora:
                turno_dt = datetime.combine(turno.fecha, turno.hora)
                if turno_dt < ahora:
                    es_vencido = True
            if es_vencido:
                turno.estado = 'NoAtendido'
                cambios += 1
        if cambios:
            session.commit()

    @staticmethod
    def listar_turnos(fecha_filtro: str | None, termino: str | None):
        session = DatabaseSession.get_instance().session
        TurnoService.actualizar_no_atendidos(session)

        query = session.query(Turno).options(joinedload(Turno.paciente)).join(Paciente)

        if fecha_filtro:
            fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            query = query.filter(Turno.fecha == fecha_obj)
        else:
            query = query.filter(Turno.fecha >= date.today())

        termino = (termino or '').strip()
        if termino:
            like_term = f"%{termino.lower()}%"
            query = query.filter(
                (Paciente.nombre.ilike(like_term)) |
                (Paciente.apellido.ilike(like_term)) |
                (Paciente.dni.ilike(like_term))
            )

        return query.order_by(Turno.fecha, Turno.hora).all()

    @staticmethod
    def crear_turno(data: dict):
        """Crea un nuevo turno con validaciones completas.
        
        Args:
            data: Dict con paciente_id, fecha, hora, duracion, detalle, estado
            
        Returns:
            Turno creado
            
        Raises:
            ValueError: Si las validaciones fallan
        """
        session = DatabaseSession.get_instance().session
        
        # Extraer y validar datos
        paciente_id = data.get('paciente_id')
        fecha = data.get('fecha')
        hora = data.get('hora')
        duracion = data.get('duracion', 30)
        detalle = data.get('detalle')
        estado = data.get('estado', 'Pendiente')
        
        # Validaciones básicas
        if not paciente_id:
            raise ValueError('El paciente es requerido')
        
        if not fecha:
            raise ValueError('La fecha es requerida')
        
        if not hora:
            raise ValueError('La hora es requerida')
        
        # Verificar que el paciente existe
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            raise ValueError(f'El paciente con ID {paciente_id} no existe')
        
        # Validar fecha no sea en el pasado
        if fecha < date.today():
            raise ValueError('No se pueden crear turnos en fechas pasadas')
        
        # Validar día laborable
        if fecha.weekday() not in TurnoService.DIAS_LABORABLES:
            raise ValueError('Solo se pueden crear turnos de lunes a sábado')
        
        # Validar horario dentro del rango permitido
        if hora < TurnoService.HORARIO_INICIO or hora >= TurnoService.HORARIO_FIN:
            raise ValueError(
                f'Los turnos solo se pueden crear entre '
                f'{TurnoService.HORARIO_INICIO.strftime("%H:%M")} y '
                f'{TurnoService.HORARIO_FIN.strftime("%H:%M")}'
            )
        
        # Validar duración
        if duracion < 5 or duracion > 480:  # Entre 5 minutos y 8 horas
            raise ValueError('La duración debe estar entre 5 y 480 minutos (8 horas)')
        
        # Validar que el turno no exceda el horario de fin
        hora_fin_turno = datetime.combine(date.today(), hora) + timedelta(minutes=duracion)
        if hora_fin_turno.time() > TurnoService.HORARIO_FIN:
            raise ValueError(
                f'El turno terminaría a las {hora_fin_turno.strftime("%H:%M")}, '
                f'después del horario de atención ({TurnoService.HORARIO_FIN.strftime("%H:%M")}). '
                f'Reduzca la duración o elija un horario más temprano.'
            )
        
        # Verificar solapamiento con otros turnos
        hay_solape, mensaje_solape, _ = TurnoService.verificar_solapamiento(
            fecha, hora, duracion
        )
        if hay_solape:
            raise ValueError(mensaje_solape)
        
        # Validar estado inicial
        if estado not in ['Pendiente', 'Confirmado']:
            estado = 'Pendiente'  # Forzar estado inicial válido
        
        # Crear turno
        turno = Turno(
            paciente_id=paciente_id,
            fecha=fecha,
            hora=hora,
            duracion=duracion,
            detalle=detalle,
            estado=estado,
        )
        session.add(turno)
        session.commit()
        return turno

    @staticmethod
    def cambiar_estado(turno_id: int, nuevo_estado: str):
        """Cambia el estado de un turno con validación de transiciones.
        
        Args:
            turno_id: ID del turno
            nuevo_estado: Nuevo estado deseado
            
        Returns:
            Tupla (turno, mensaje_error). Si hay error, turno es None.
        """
        session = DatabaseSession.get_instance().session
        turno = session.get(Turno, turno_id)
        if not turno:
            return None, 'Turno no encontrado'

        estado_anterior = turno.estado or 'Pendiente'
        
        # Validar transición de estado usando la matriz
        es_valida, mensaje_error = TurnoService.validar_transicion_estado(
            estado_anterior, nuevo_estado
        )
        if not es_valida:
            return None, mensaje_error
        
        # Validación adicional: turnos pasados solo pueden marcarse como Atendido o NoAtendido
        if turno.fecha < date.today():
            if nuevo_estado not in ['Atendido', 'NoAtendido']:
                return None, (
                    f'Los turnos de fechas pasadas solo pueden marcarse como '
                    f'"Atendido" o "NoAtendido", no como "{nuevo_estado}"'
                )
        
        # Aplicar cambio de estado
        turno.estado = nuevo_estado

        # Registrar cambio de estado
        cambio = CambioEstado(
            turno_id=turno.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            fecha_cambio=datetime.now(),
            motivo='Cambio de estado desde interfaz de usuario'
        )

        session.add(cambio)
        session.commit()
        return turno, None

    @staticmethod
    def eliminar_turno(turno_id: int):
        session = DatabaseSession.get_instance().session
        turno = session.get(Turno, turno_id)
        if not turno:
            return None, 'Turno no encontrado'
        estado_actual = turno.estado or 'Pendiente'
        if estado_actual != 'Pendiente':
            return None, f'Solo se pueden eliminar turnos Pendientes. Este turno está: {estado_actual}'
        session.delete(turno)
        session.commit()
        return turno, None
    
    @staticmethod
    def obtener_estadisticas_turnos() -> Dict[str, int]:
        """
        Obtiene estadísticas de turnos.
        
        Returns:
            Dict con estadísticas
        """
        total_turnos = Turno.query.count()
        turnos_hoy = Turno.query.filter_by(fecha=date.today()).count()
        
        # Turnos por estado
        estados = Estado.query.all()
        turnos_por_estado = {}
        
        for estado in estados:
            count = Turno.query.filter_by(estado_id=estado.id).count()
            turnos_por_estado[estado.nombre] = count
        
        return {
            'total_turnos': total_turnos,
            'turnos_hoy': turnos_hoy,
            **turnos_por_estado
        }
    
    @staticmethod
    def cancelar_turno(turno_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Cancela un turno.
        
        Args:
            turno_id: ID del turno a cancelar
            motivo: Motivo de la cancelación
            
        Returns:
            Dict con el resultado de la operación
        """
        return TurnoService.cambiar_estado_turno(
            turno_id, 'Cancelado', motivo or 'Turno cancelado'
        )
    
    @staticmethod
    def confirmar_turno(turno_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Confirma un turno.
        
        Args:
            turno_id: ID del turno a confirmar
            motivo: Motivo de la confirmación
            
        Returns:
            Dict con el resultado de la operación
        """
        return TurnoService.cambiar_estado_turno(
            turno_id, 'Confirmado', motivo or 'Turno confirmado'
        )
    
    @staticmethod
    def completar_turno(turno_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Marca un turno como completado.
        
        Args:
            turno_id: ID del turno a completar
            motivo: Motivo de la finalización
            
        Returns:
            Dict con el resultado de la operación
        """
        return TurnoService.cambiar_estado_turno(
            turno_id, 'Completado', motivo or 'Turno completado'
        )
