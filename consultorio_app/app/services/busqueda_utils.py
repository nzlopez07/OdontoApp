"""
Utilidades para búsqueda y normalización de texto.

Este módulo contiene funciones para realizar búsquedas más flexibles
que ignoren diferencias de mayúsculas, tildes y caracteres especiales.
"""

import unicodedata
import re
from typing import List
from sqlalchemy import func, or_, and_
from app.models import Paciente


class BusquedaUtils:
    """Utilidades para búsqueda de texto."""
    
    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Normaliza un texto removiendo tildes, convirtiendo a minúsculas
        y eliminando caracteres especiales.
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        if not texto:
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Remover tildes y caracteres especiales
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        
        # Remover caracteres no alfanuméricos excepto espacios
        texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
        
        # Limpiar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    @staticmethod
    def buscar_pacientes(termino_busqueda: str) -> List[Paciente]:
        """
        Busca pacientes por nombre, apellido o DNI de forma flexible.
        
        Args:
            termino_busqueda: Término de búsqueda
            
        Returns:
            Lista de pacientes que coinciden con la búsqueda
        """
        if not termino_busqueda or not termino_busqueda.strip():
            return Paciente.query.all()
        
        # Normalizar término de búsqueda
        termino_normalizado = BusquedaUtils.normalizar_texto(termino_busqueda)
        
        # Si el término parece ser un DNI (solo números), buscar por DNI
        if termino_normalizado.isdigit():
            return Paciente.query.filter(
                Paciente.dni.like(f'%{termino_normalizado}%')
            ).all()
        
        # Buscar por nombre y apellido usando LIKE con wildcards
        # Separar las palabras del término de búsqueda
        palabras = termino_normalizado.split()
        
        if len(palabras) == 1:
            # Una sola palabra: buscar en nombre O apellido
            palabra = palabras[0]
            return Paciente.query.filter(
                or_(
                    func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                        Paciente.nombre, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{palabra}%'),
                    func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                        Paciente.apellido, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{palabra}%')
                )
            ).all()
        
        elif len(palabras) == 2:
            # Dos palabras: primera puede ser nombre y segunda apellido, o viceversa
            palabra1, palabra2 = palabras
            return Paciente.query.filter(
                or_(
                    # Nombre + Apellido
                    and_(
                        func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                            Paciente.nombre, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{palabra1}%'),
                        func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                            Paciente.apellido, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{palabra2}%')
                    ),
                    # Apellido + Nombre
                    and_(
                        func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                            Paciente.apellido, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{palabra1}%'),
                        func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                            Paciente.nombre, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{palabra2}%')
                    ),
                    # Solo en nombre
                    func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                        Paciente.nombre, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{termino_normalizado.replace(" ", "%")}%'),
                    # Solo en apellido
                    func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                        Paciente.apellido, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{termino_normalizado.replace(" ", "%")}%')
                )
            ).all()
        
        else:
            # Más de dos palabras: buscar como una cadena completa
            termino_con_wildcards = termino_normalizado.replace(' ', '%')
            return Paciente.query.filter(
                or_(
                    func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                        Paciente.nombre, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{termino_con_wildcards}%'),
                    func.lower(func.replace(func.replace(func.replace(func.replace(func.replace(
                        Paciente.apellido, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')).like(f'%{termino_con_wildcards}%')
                )
            ).all()
    
    @staticmethod
    def buscar_pacientes_simple(termino_busqueda: str) -> List[Paciente]:
        """
        Versión simplificada de búsqueda para compatibilidad con más bases de datos.
        
        Args:
            termino_busqueda: Término de búsqueda
            
        Returns:
            Lista de pacientes que coinciden con la búsqueda
        """
        if not termino_busqueda or not termino_busqueda.strip():
            return Paciente.query.all()
        
        # Para la búsqueda simple, obtenemos todos los pacientes y filtramos en Python
        todos_pacientes = Paciente.query.all()
        termino_normalizado = BusquedaUtils.normalizar_texto(termino_busqueda)
        
        pacientes_encontrados = []
        
        for paciente in todos_pacientes:
            # Normalizar nombre y apellido del paciente
            nombre_normalizado = BusquedaUtils.normalizar_texto(paciente.nombre or "")
            apellido_normalizado = BusquedaUtils.normalizar_texto(paciente.apellido or "")
            dni_str = str(paciente.dni or "")
            
            # Verificar si el término está en nombre, apellido o DNI
            if (termino_normalizado in nombre_normalizado or 
                termino_normalizado in apellido_normalizado or 
                termino_normalizado in dni_str or
                termino_normalizado in f"{nombre_normalizado} {apellido_normalizado}" or
                termino_normalizado in f"{apellido_normalizado} {nombre_normalizado}"):
                pacientes_encontrados.append(paciente)
        
        return pacientes_encontrados
