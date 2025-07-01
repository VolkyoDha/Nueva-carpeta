"""
Funciones auxiliares para manejo de archivos JSON.
"""
import json

def leer_json(ruta):
    """Lee un archivo JSON y retorna su contenido."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def escribir_json(ruta, datos):
    """Escribe datos en un archivo JSON."""
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2) 