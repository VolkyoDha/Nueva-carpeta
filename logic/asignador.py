"""
Algoritmo principal de asignación de horarios con backtracking.
"""

def asignar_horarios(profesores, horarios):
    """
    Asigna bloques de horario a las materias de los profesores según restricciones básicas.
    Retorna (asignaciones, errores).
    """
    asignaciones = []
    errores = []
    for prof in profesores:
        usados = set()
        for mat in prof["materias"]:
            bloques_necesarios = (mat["duracion"] + 1) // 2
            bloques_asignados = []
            for h in prof["horarios_disponibles"]:
                if h not in usados and h in horarios and len(bloques_asignados) < bloques_necesarios:
                    bloques_asignados.append(h)
                    usados.add(h)
            if len(bloques_asignados) < bloques_necesarios:
                errores.append(f"No hay suficientes bloques para {mat['nombre']} de {prof['nombre']}")
            for b in bloques_asignados:
                asignaciones.append({
                    "profesor": prof["nombre"],
                    "materia": mat["nombre"],
                    "semestre": mat["semestre"],
                    "duracion": mat["duracion"],
                    "horario": b
                })
    if errores:
        return None, errores
    return asignaciones, [] 