"""
Archivo de prueba para verificar la funcionalidad del gestor de materias.
Este archivo se puede ejecutar independientemente para probar las funciones.
"""

import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.materias_manager import MateriasManager


def test_materias_manager():
    """Prueba las funciones básicas del gestor de materias."""
    print("🧪 Probando MateriasManager...")
    
    # Crear instancia del gestor
    manager = MateriasManager("test_materias.json")
    
    # Prueba 1: Cargar materias existentes
    print("\n1. Cargando materias existentes...")
    materias = manager.load_materias()
    print(f"   Materias cargadas: {len(materias)}")
    
    # Prueba 2: Agregar una nueva materia
    print("\n2. Agregando nueva materia...")
    nueva_materia = {
        'codigo': 'TEST001',
        'nombre': 'Materia de Prueba',
        'semestre': 1,
        'horas_semanales': 4,
        'horas_semestrales': 64
    }
    
    success, message = manager.add_materia(nueva_materia)
    print(f"   Resultado: {success} - {message}")
    
    # Prueba 3: Validar materia inválida
    print("\n3. Probando validación de materia inválida...")
    materia_invalida = {
        'codigo': '',
        'nombre': 'Materia Inválida',
        'semestre': 15,  # Semestre inválido
        'horas_semanales': -5,  # Horas negativas
        'horas_semestrales': 0  # Horas cero
    }
    
    is_valid, error_msg = manager.validate_materia(materia_invalida)
    print(f"   Válida: {is_valid}")
    print(f"   Error: {error_msg}")
    
    # Prueba 4: Buscar materia por código
    print("\n4. Buscando materia por código...")
    materia_encontrada = manager.get_materia_by_codigo('TEST001')
    if materia_encontrada:
        print(f"   Materia encontrada: {materia_encontrada['nombre']}")
    else:
        print("   Materia no encontrada")
    
    # Prueba 5: Obtener materias por semestre
    print("\n5. Obteniendo materias del semestre 1...")
    materias_semestre = manager.get_materias_by_semestre(1)
    print(f"   Materias del semestre 1: {len(materias_semestre)}")
    
    # Prueba 6: Actualizar materia
    print("\n6. Actualizando materia...")
    materia_actualizada = {
        'codigo': 'TEST001',
        'nombre': 'Materia de Prueba Actualizada',
        'semestre': 2,
        'horas_semanales': 6,
        'horas_semestrales': 96
    }
    
    success, message = manager.update_materia('TEST001', materia_actualizada)
    print(f"   Resultado: {success} - {message}")
    
    # Prueba 7: Eliminar materia
    print("\n7. Eliminando materia...")
    success, message = manager.delete_materia('TEST001')
    print(f"   Resultado: {success} - {message}")
    
    # Limpiar archivo de prueba
    try:
        os.remove("test_materias.json")
        print("\n✅ Archivo de prueba eliminado")
    except FileNotFoundError:
        pass
    
    print("\n🎉 Todas las pruebas completadas!")


if __name__ == "__main__":
    test_materias_manager() 