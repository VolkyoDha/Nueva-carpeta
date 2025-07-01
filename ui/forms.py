"""
Formularios de entrada de profesores y materias para Streamlit.
"""
import streamlit as st

HORARIOS_BASE = [
    "Lunes 7-9", "Lunes 9-11", "Lunes 11-13", "Lunes 13-15",
    "Martes 7-9", "Martes 9-11", "Martes 11-13", "Martes 13-15",
    "Miércoles 7-9", "Miércoles 9-11", "Miércoles 11-13", "Miércoles 13-15",
    "Jueves 7-9", "Jueves 9-11", "Jueves 11-13", "Jueves 13-15",
    "Viernes 7-9", "Viernes 9-11", "Viernes 11-13", "Viernes 13-15"
]
DURACIONES = [1, 2, 4, 6]

def formulario_profesor():
    """
    Formulario para ingresar un profesor y sus materias.
    Retorna un dict con la estructura solicitada si todo está completo, None si falta algún campo.
    """
    with st.form("form_profesor", clear_on_submit=True):
        nombre = st.text_input("Nombre del profesor")
        horarios = st.multiselect("Horarios disponibles", HORARIOS_BASE)
        n_materias = st.slider("¿Cuántas materias dicta?", min_value=1, max_value=10, value=1)
        materias = []
        for i in range(n_materias):
            st.markdown(f"**Materia #{i+1}**")
            nombre_mat = st.text_input(f"Nombre de la materia #{i+1}", key=f"nombre_mat_{i}")
            semestre = st.number_input(f"Semestre de la materia #{i+1}", min_value=1, max_value=12, value=1, step=1, key=f"semestre_mat_{i}")
            duracion = st.selectbox(f"Duración semanal (horas) de la materia #{i+1}", DURACIONES, key=f"duracion_mat_{i}")
            materias.append({
                "nombre": nombre_mat,
                "semestre": semestre,
                "duracion": duracion
            })
        submit = st.form_submit_button("Agregar profesor")
        if submit:
            if not nombre or not horarios or any(not m["nombre"] or not m["semestre"] or not m["duracion"] for m in materias):
                st.warning("Por favor, complete todos los campos antes de agregar el profesor.")
                return None
            return {
                "nombre": nombre,
                "horarios_disponibles": horarios,
                "materias": materias
            }
    return None

def formulario_materia():
    """Formulario para ingresar datos de una materia."""
    pass 