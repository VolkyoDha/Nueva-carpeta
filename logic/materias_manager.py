"""
Módulo para gestionar las materias del currículum.
Maneja la lectura, escritura y validación de datos de materias.
"""

import json
import os
from typing import List, Dict, Optional, Tuple
import streamlit as st


class MateriasManager:
    """Clase para gestionar las operaciones CRUD de materias."""
    
    def __init__(self, file_path: str = "resources/materias.json"):
        """
        Inicializa el gestor de materias.
        
        Args:
            file_path: Ruta al archivo JSON de materias
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Asegura que el archivo JSON existe, creándolo si es necesario."""
        if not os.path.exists(self.file_path):
            # Crear directorio solo si no es el directorio actual
            dir_path = os.path.dirname(self.file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            self._save_materias([])
    
    def load_materias(self) -> List[Dict]:
        """
        Carga las materias desde el archivo JSON.
        
        Returns:
            Lista de diccionarios con los datos de las materias
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Error al cargar materias: {e}")
            return []
    
    def _save_materias(self, materias: List[Dict]) -> bool:
        """
        Guarda las materias en el archivo JSON.
        
        Args:
            materias: Lista de diccionarios con los datos de las materias
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(materias, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error al guardar materias: {e}")
            return False
    
    def validate_materia(self, materia: Dict) -> Tuple[bool, str]:
        """
        Valida los datos de una materia.
        
        Args:
            materia: Diccionario con los datos de la materia
            
        Returns:
            Tupla con (es_válido, mensaje_error)
        """
        # Validar campos requeridos
        required_fields = ['codigo', 'nombre', 'semestre', 'horas_semanales', 'horas_semestrales']
        for field in required_fields:
            if field not in materia or not materia[field]:
                return False, f"El campo '{field}' es obligatorio"
        
        # Validar código (no vacío y único)
        if not isinstance(materia['codigo'], str) or len(materia['codigo'].strip()) == 0:
            return False, "El código debe ser una cadena no vacía"
        
        # Validar nombre (no vacío)
        if not isinstance(materia['nombre'], str) or len(materia['nombre'].strip()) == 0:
            return False, "El nombre debe ser una cadena no vacía"
        
        # Validar semestre (1-10)
        try:
            semestre = int(materia['semestre'])
            if semestre < 1 or semestre > 10:
                return False, "El semestre debe estar entre 1 y 10"
        except (ValueError, TypeError):
            return False, "El semestre debe ser un número entero"
        
        # Validar horas semanales (positivo)
        try:
            horas_semanales = int(materia['horas_semanales'])
            if horas_semanales <= 0:
                return False, "Las horas semanales deben ser un número positivo"
        except (ValueError, TypeError):
            return False, "Las horas semanales deben ser un número entero"
        
        # Validar horas semestrales (positivo)
        try:
            horas_semestrales = int(materia['horas_semestrales'])
            if horas_semestrales <= 0:
                return False, "Las horas semestrales deben ser un número positivo"
        except (ValueError, TypeError):
            return False, "Las horas semestrales deben ser un número entero"
        
        return True, ""
    
    def add_materia(self, materia: Dict) -> Tuple[bool, str]:
        """
        Agrega una nueva materia.
        
        Args:
            materia: Diccionario con los datos de la materia
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        # Validar datos
        is_valid, error_msg = self.validate_materia(materia)
        if not is_valid:
            return False, error_msg
        
        # Verificar que el código no exista
        materias = self.load_materias()
        if any(m['codigo'] == materia['codigo'] for m in materias):
            return False, f"Ya existe una materia con el código '{materia['codigo']}'"
        
        # Agregar la materia
        materias.append(materia)
        
        # Guardar
        if self._save_materias(materias):
            return True, f"Materia '{materia['nombre']}' agregada correctamente"
        else:
            return False, "Error al guardar la materia"
    
    def update_materia(self, codigo_original: str, materia_actualizada: Dict) -> Tuple[bool, str]:
        """
        Actualiza una materia existente.
        
        Args:
            codigo_original: Código de la materia a actualizar
            materia_actualizada: Diccionario con los datos actualizados
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        # Validar datos
        is_valid, error_msg = self.validate_materia(materia_actualizada)
        if not is_valid:
            return False, error_msg
        
        # Cargar materias
        materias = self.load_materias()
        
        # Buscar la materia
        materia_index = None
        for i, materia in enumerate(materias):
            if materia['codigo'] == codigo_original:
                materia_index = i
                break
        
        if materia_index is None:
            return False, f"No se encontró la materia con código '{codigo_original}'"
        
        # Verificar que el nuevo código no exista (si cambió)
        nuevo_codigo = materia_actualizada['codigo']
        if nuevo_codigo != codigo_original:
            if any(m['codigo'] == nuevo_codigo for m in materias):
                return False, f"Ya existe una materia con el código '{nuevo_codigo}'"
        
        # Actualizar la materia
        materias[materia_index] = materia_actualizada
        
        # Guardar
        if self._save_materias(materias):
            return True, f"Materia '{materia_actualizada['nombre']}' actualizada correctamente"
        else:
            return False, "Error al guardar la materia"
    
    def delete_materia(self, codigo: str) -> Tuple[bool, str]:
        """
        Elimina una materia.
        
        Args:
            codigo: Código de la materia a eliminar
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        # Cargar materias
        materias = self.load_materias()
        
        # Buscar y eliminar la materia
        materia_encontrada = None
        for materia in materias:
            if materia['codigo'] == codigo:
                materia_encontrada = materia
                break
        
        if not materia_encontrada:
            return False, f"No se encontró la materia con código '{codigo}'"
        
        # Eliminar la materia
        materias = [m for m in materias if m['codigo'] != codigo]
        
        # Guardar
        if self._save_materias(materias):
            return True, f"Materia '{materia_encontrada['nombre']}' eliminada correctamente"
        else:
            return False, "Error al eliminar la materia"
    
    def get_materia_by_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Obtiene una materia por su código.
        
        Args:
            codigo: Código de la materia
            
        Returns:
            Diccionario con los datos de la materia o None si no existe
        """
        materias = self.load_materias()
        for materia in materias:
            if materia['codigo'] == codigo:
                return materia
        return None
    
    def get_materias_by_semestre(self, semestre: int) -> List[Dict]:
        """
        Obtiene todas las materias de un semestre específico.
        
        Args:
            semestre: Número del semestre (1-10)
            
        Returns:
            Lista de materias del semestre
        """
        materias = self.load_materias()
        return [m for m in materias if m['semestre'] == semestre]
    
    def get_all_codigos(self) -> List[str]:
        """
        Obtiene todos los códigos de materias.
        
        Returns:
            Lista de códigos de materias
        """
        materias = self.load_materias()
        return [m['codigo'] for m in materias] 