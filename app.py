"""
App Streamlit para asignación de horarios académicos con duración semanal por materia.
Autor: Proyecto educativo
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional

# ------------------- Configuración de la página -------------------
st.set_page_config(page_title="Asignación de Horarios Universitarios", layout="centered")

# ------------------- Constantes -------------------
HORARIOS = [
    "Lunes 7-9", "Lunes 9-11", "Lunes 11-13", "Lunes 13-15",
    "Martes 7-9", "Martes 9-11", "Martes 11-13", "Martes 13-15",
    "Miércoles 7-9", "Miércoles 9-11", "Miércoles 11-13", "Miércoles 13-15",
    "Jueves 7-9", "Jueves 9-11", "Jueves 11-13", "Jueves 13-15",
    "Viernes 7-9", "Viernes 9-11", "Viernes 11-13", "Viernes 13-15",
]
DURACIONES = [1, 2, 4, 6]  # Horas semanales posibles por materia

# ------------------- Utilidades -------------------
def es_horario_almuerzo(horario: str) -> bool:
    """Devuelve True si el horario incluye el bloque de 12-13."""
    partes = horario.split()
    if len(partes) != 2:
        return False
    horas = partes[1].split("-")
    if len(horas) != 2:
        return False
    inicio = int(horas[0])
    fin = int(horas[1])
    return (inicio < 13 and fin > 12)

def obtener_dia(horario: str) -> str:
    return horario.split()[0]

# ------------------- Sección: Ingreso de profesores -------------------
def seccion_ingreso_profesores():
    st.markdown("<h2 style='text-align:center;'>Ingreso de Profesores y Materias</h2>", unsafe_allow_html=True)
    if 'profesores' not in st.session_state:
        st.session_state['profesores'] = []
    with st.form("form_profesor", clear_on_submit=True):
        nombre_prof = st.text_input("Nombre del profesor")
        horarios_disp = st.multiselect("Horarios disponibles", HORARIOS)
        st.markdown("<h3>Materias que dicta el profesor</h3>", unsafe_allow_html=True)
        num_materias = st.slider("¿Cuántas materias dicta el profesor?", min_value=1, max_value=10, value=1)
        materias = []
        for i in range(num_materias):
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                nombre = st.text_input(f"Nombre de la materia #{i+1}", key=f"nombre_mat_{i}")
            with col2:
                semestre = st.number_input(f"Semestre", min_value=1, max_value=12, value=1, step=1, key=f"semestre_mat_{i}")
            with col3:
                duracion = st.selectbox(
                    f"Duración semanal (horas)",
                    options=DURACIONES,
                    key=f"duracion_mat_{i}"
                )
            materias.append({"nombre": nombre, "semestre": semestre, "duracion": duracion})
        agregar = st.form_submit_button("Agregar profesor")
        if agregar:
            if not nombre_prof or not horarios_disp or any(not m['nombre'] or not m['semestre'] or not m['duracion'] for m in materias):
                st.error("Por favor, complete todos los campos para el profesor y sus materias.")
            else:
                st.session_state['profesores'].append({
                    'nombre': nombre_prof,
                    'materias': materias,
                    'horarios': horarios_disp
                })
                st.success(f"Profesor {nombre_prof} agregado.")

    # Mostrar profesores agregados
    if st.session_state['profesores']:
        st.markdown("<h4 style='text-align:center;'>Profesores ingresados</h4>", unsafe_allow_html=True)
        for prof in st.session_state['profesores']:
            st.write(f"- **{prof['nombre']}**: {[m['nombre'] for m in prof['materias']]}")

# ------------------- Algoritmo de asignación -------------------
def asignar_horarios(profesores: List[Dict]) -> Optional[List[Dict]]:
    """
    Asigna bloques de horario a todas las materias de todos los profesores según su duración semanal.
    Cada materia recibe tantos bloques como necesita (1 bloque = 2h).
    Devuelve una lista de asignaciones si es posible, o None si no hay solución.
    Cada asignación es un dict: {'Día', 'Horario', 'Materia', 'Semestre', 'Profesor'}
    """
    # Preprocesar: eliminar horarios de almuerzo y preparar lista de tareas
    tareas = []  # Cada tarea: (profesor_idx, materia_idx, bloque_idx)
    disponibilidad = []  # Por tarea, los horarios disponibles
    for p_idx, prof in enumerate(profesores):
        horarios_validos = [h for h in prof['horarios'] if not es_horario_almuerzo(h)]
        for m_idx, mat in enumerate(prof['materias']):
            bloques_necesarios = (mat['duracion'] + 1) // 2  # Redondea hacia arriba si es impar
            for b in range(bloques_necesarios):
                tareas.append((p_idx, m_idx, b))
                disponibilidad.append(horarios_validos)
    # Estado para backtracking
    asignaciones = [None] * len(tareas)  # Horario asignado a cada tarea
    usados_por_profesor = [set() for _ in profesores]  # Horarios ya usados por cada profesor
    horas_por_profesor = [0 for _ in profesores]  # Contador de bloques asignados
    materias_por_dia = [{} for _ in profesores]  # Por profesor, cuántas materias por día
    horarios_por_semestre = dict()  # (semestre, horario) -> tarea_idx
    horarios_global = dict()  # (profesor, horario) -> tarea_idx
    bloques_por_materia = dict()  # (profesor_idx, materia_idx) -> set de horarios

    def backtrack(idx):
        if idx == len(tareas):
            return True
        p_idx, m_idx, b_idx = tareas[idx]
        prof = profesores[p_idx]
        mat = prof['materias'][m_idx]
        semestre = mat['semestre']
        for horario in disponibilidad[idx]:
            dia = obtener_dia(horario)
            # Restricción: no usar horario de almuerzo (ya filtrado)
            # Restricción: no más de 40h/semana (20 bloques)
            if horas_por_profesor[p_idx] >= 20:
                continue
            # Restricción: un horario no puede usarse dos veces por el mismo profesor
            if horario in usados_por_profesor[p_idx]:
                continue
            # Restricción: no más de 2 materias en el mismo día
            if materias_por_dia[p_idx].get(dia, 0) >= 2:
                continue
            # Restricción: dos materias del mismo semestre no pueden estar en el mismo horario
            if (semestre, horario) in horarios_por_semestre:
                continue
            # Restricción: un profesor no puede estar en dos materias al mismo tiempo
            if (p_idx, horario) in horarios_global:
                continue
            # Restricción: no repetir bloques para la misma materia
            if (p_idx, m_idx) in bloques_por_materia and horario in bloques_por_materia[(p_idx, m_idx)]:
                continue
            # Asignar
            asignaciones[idx] = horario
            usados_por_profesor[p_idx].add(horario)
            horas_por_profesor[p_idx] += 1
            materias_por_dia[p_idx][dia] = materias_por_dia[p_idx].get(dia, 0) + 1
            horarios_por_semestre[(semestre, horario)] = idx
            horarios_global[(p_idx, horario)] = idx
            if (p_idx, m_idx) not in bloques_por_materia:
                bloques_por_materia[(p_idx, m_idx)] = set()
            bloques_por_materia[(p_idx, m_idx)].add(horario)
            if backtrack(idx + 1):
                return True
            # Backtrack
            asignaciones[idx] = None
            usados_por_profesor[p_idx].remove(horario)
            horas_por_profesor[p_idx] -= 1
            materias_por_dia[p_idx][dia] -= 1
            if materias_por_dia[p_idx][dia] == 0:
                del materias_por_dia[p_idx][dia]
            del horarios_por_semestre[(semestre, horario)]
            del horarios_global[(p_idx, horario)]
            bloques_por_materia[(p_idx, m_idx)].remove(horario)
        return False

    if backtrack(0):
        resultado = []
        for idx, (p_idx, m_idx, b_idx) in enumerate(tareas):
            prof = profesores[p_idx]
            mat = prof['materias'][m_idx]
            horario = asignaciones[idx]
            dia = obtener_dia(horario)
            resultado.append({
                'Profesor': prof['nombre'],
                'Materia': mat['nombre'],
                'Semestre': mat['semestre'],
                'Duración': mat['duracion'],
                'Día': dia,
                'Horario': horario
            })
        return resultado
    else:
        return None

# ------------------- Cálculo de carga horaria -------------------
def calcular_carga_horaria(asignaciones: List[Dict]) -> pd.DataFrame:
    """Calcula la carga horaria por profesor a partir de la lista de asignaciones."""
    df = pd.DataFrame(asignaciones)
    resumen = df.groupby('Profesor').agg(
        Bloques_Asignados = ('Horario', 'count')
    ).reset_index()
    resumen['Horas_Totales'] = resumen['Bloques_Asignados'] * 2
    return resumen

# ------------------- Sección: Cálculo y visualización de resultados -------------------
def seccion_calculo_resultado():
    st.markdown("<h2 style='text-align:center;'>Asignación y Carga Horaria</h2>", unsafe_allow_html=True)
    profesores = st.session_state.get('profesores', [])
    if not profesores:
        st.info("Agregue al menos un profesor para calcular la asignación de horarios.")
        return
    calcular = st.button("Calcular horarios", use_container_width=True)
    if calcular:
        resultado = asignar_horarios(profesores)
        if resultado:
            st.success("¡Asignación exitosa!")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<b>Bloques asignados por materia</b>", unsafe_allow_html=True)
                df = pd.DataFrame(resultado)
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col2:
                st.markdown("<b>Carga horaria por profesor</b>", unsafe_allow_html=True)
                resumen = calcular_carga_horaria(resultado)
                st.dataframe(resumen, use_container_width=True, hide_index=True)
        else:
            st.error("No se encontró una combinación válida de horarios para las restricciones dadas.")

# ------------------- Main -------------------
def main():
    st.markdown("<h1 style='text-align:center;'>Asignación de Horarios Universitarios</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    seccion_ingreso_profesores()
    st.markdown("<hr>", unsafe_allow_html=True)
    seccion_calculo_resultado()

if __name__ == "__main__":
    main() 