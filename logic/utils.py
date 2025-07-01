"""
Funciones auxiliares para manejo de archivos JSON y gestión de profesores y materias.
"""
import json

RUTA_PROFESORES = "data/profesores.json"
RUTA_MATERIAS = "data/materias.json"
RUTA_MALLA_CURRICULAR = "data/materias.json"

def leer_json(ruta):
    """Lee un archivo JSON y retorna su contenido."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def escribir_json(ruta, datos):
    """Escribe datos en un archivo JSON."""
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def guardar_profesores(lista):
    """Guarda la lista completa de profesores en el archivo JSON."""
    with open(RUTA_PROFESORES, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def cargar_profesores():
    """Carga y retorna la lista de profesores desde el archivo JSON."""
    try:
        with open(RUTA_PROFESORES, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def eliminar_profesor(nombre):
    """Elimina un profesor por nombre y actualiza el archivo JSON."""
    profesores = cargar_profesores()
    profesores = [p for p in profesores if p['nombre'] != nombre]
    guardar_profesores(profesores)

def actualizar_profesor(nombre, nuevo_profesor):
    """Actualiza los datos de un profesor identificado por nombre."""
    profesores = cargar_profesores()
    for i, p in enumerate(profesores):
        if p['nombre'] == nombre:
            profesores[i] = nuevo_profesor
            break
    guardar_profesores(profesores)

# --- Materias ---
def guardar_materias(lista):
    """Guarda la lista completa de materias en el archivo JSON."""
    with open(RUTA_MATERIAS, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def cargar_materias():
    """Carga y retorna la lista de materias desde el archivo JSON."""
    try:
        with open(RUTA_MATERIAS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def eliminar_materia(nombre):
    """Elimina una materia por nombre y actualiza el archivo JSON."""
    materias = cargar_materias()
    materias = [m for m in materias if m['nombre'] != nombre]
    guardar_materias(materias)

def actualizar_materia(nombre, nueva_materia):
    """Actualiza los datos de una materia identificada por nombre."""
    materias = cargar_materias()
    for i, m in enumerate(materias):
        if m['nombre'] == nombre:
            materias[i] = nueva_materia
            break
    guardar_materias(materias)

# --- Malla Curricular ---
def cargar_malla_curricular():
    """Carga y retorna la malla curricular completa desde el archivo JSON."""
    try:
        with open(RUTA_MALLA_CURRICULAR, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def obtener_materias_por_semestre(semestre):
    """Retorna las materias de un semestre específico."""
    malla = cargar_malla_curricular()
    return [m for m in malla if m['semestre'] == semestre]

def buscar_materia_por_codigo(codigo):
    """Busca una materia por su código y retorna la materia completa."""
    malla = cargar_malla_curricular()
    for materia in malla:
        if materia['codigo'] == codigo:
            return materia
    return None

def buscar_materia_por_nombre(nombre):
    """Busca una materia por su nombre y retorna la materia completa."""
    malla = cargar_malla_curricular()
    for materia in malla:
        if materia['nombre'].lower() == nombre.lower():
            return materia
    return None 