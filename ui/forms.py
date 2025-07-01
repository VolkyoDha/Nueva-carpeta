"""
ui/forms.py - Formularios y gestión de profesores y materias para la app de asignación de horarios universitarios.
Incluye formularios para registrar, editar, eliminar y seleccionar profesores y materias.
"""
import streamlit as st
from logic import utils
# from ui.layout import tarjeta_profesor, tarjeta_materia
from logic.asignador import asignar_horarios
import pandas as pd

HORARIOS_BASE = [
    "Lunes 7-9", "Lunes 9-11", "Lunes 11-13", "Lunes 13-15",
    "Martes 7-9", "Martes 9-11", "Martes 11-13", "Martes 13-15",
    "Miércoles 7-9", "Miércoles 9-11", "Miércoles 11-13", "Miércoles 13-15",
    "Jueves 7-9", "Jueves 9-11", "Jueves 11-13", "Jueves 13-15",
    "Viernes 7-9", "Viernes 9-11", "Viernes 11-13", "Viernes 13-15"
]
DURACIONES = [1, 2, 4, 6]

def formulario_profesor(default=None):
    """
    Formulario para ingresar o editar un profesor y sus materias.
    Si default se provee, se usa para valores iniciales (edición).
    """
    if default is None:
        nombre = st.text_input("Nombre del profesor")
        horarios = st.multiselect("Horarios disponibles", HORARIOS_BASE)
        n_materias = st.slider("¿Cuántas materias dicta?", min_value=1, max_value=10, value=1)
        materias_default = [{} for _ in range(n_materias)]
    else:
        nombre = st.text_input("Nombre del profesor", value=default['nombre'], key=f"edit_nombre_{default['nombre']}")
        horarios = st.multiselect("Horarios disponibles", HORARIOS_BASE, default=default['horarios_disponibles'], key=f"edit_horarios_{default['nombre']}")
        n_materias = st.slider("¿Cuántas materias dicta?", min_value=1, max_value=10, value=len(default['materias']), key=f"edit_nmat_{default['nombre']}")
        materias_default = default['materias'][:n_materias] + [{} for _ in range(n_materias - len(default['materias']))]
    materias = []
    for i in range(n_materias):
        st.markdown(f"**Materia #{i+1}**")
        nombre_mat = st.text_input(f"Nombre de la materia #{i+1}", value=materias_default[i].get('nombre', ''), key=f"mat_nombre_{nombre}_{i}")
        semestre = st.number_input(f"Semestre de la materia #{i+1}", min_value=1, max_value=12, value=materias_default[i].get('semestre', 1), step=1, key=f"mat_sem_{nombre}_{i}")
        duracion = st.selectbox(f"Duración semanal (horas) de la materia #{i+1}", DURACIONES, index=DURACIONES.index(materias_default[i].get('duracion', 1)) if materias_default[i].get('duracion') in DURACIONES else 0, key=f"mat_dur_{nombre}_{i}")
        materias.append({"nombre": nombre_mat, "semestre": semestre, "duracion": duracion})
    return nombre, horarios, materias

def formulario_materia(default=None):
    """
    Formulario para ingresar o editar una materia.
    Si default se provee, se usa para valores iniciales (edición).
    """
    if default is None:
        nombre = st.text_input("Nombre de la materia")
        duracion = st.selectbox("Duración semanal (horas)", DURACIONES)
        semestre = st.number_input("Semestre", min_value=1, max_value=12, value=1, step=1)
    else:
        nombre = st.text_input("Nombre de la materia", value=default['nombre'], key=f"edit_mat_nombre_{default['nombre']}")
        duracion = st.selectbox("Duración semanal (horas)", DURACIONES, index=DURACIONES.index(default['duracion']) if default['duracion'] in DURACIONES else 0, key=f"edit_mat_dur_{default['nombre']}")
        semestre = st.number_input("Semestre", min_value=1, max_value=12, value=default['semestre'], step=1, key=f"edit_mat_sem_{default['nombre']}")
    return nombre, duracion, semestre

def formulario_profesor_con_malla(default=None):
    """
    Formulario para registrar profesor seleccionando materias desde la malla curricular.
    Permite seleccionar materias por semestre y muestra automáticamente las horas.
    """
    # Cargar malla curricular
    malla = utils.cargar_malla_curricular()
    if not malla:
        st.error("No se pudo cargar la malla curricular.")
        return None, None, None

    # Datos básicos del profesor
    if default is None:
        nombre = st.text_input("Nombre del profesor")
        horarios = st.multiselect("Horarios disponibles", HORARIOS_BASE)
    else:
        nombre = st.text_input("Nombre del profesor", value=default['nombre'], key=f"edit_nombre_{default['nombre']}")
        horarios = st.multiselect("Horarios disponibles", HORARIOS_BASE, default=default['horarios_disponibles'], key=f"edit_horarios_{default['nombre']}")

    # Selección de materias por semestre
    st.markdown("### Selección de materias desde la malla curricular")
    
    # Obtener semestres únicos
    semestres = sorted(list(set([m['semestre'] for m in malla])))
    
    materias_seleccionadas = []
    
    for semestre in semestres:
        materias_semestre = utils.obtener_materias_por_semestre(semestre)
        if materias_semestre:
            with st.expander(f"Semestre {semestre}"):
                # Crear opciones para el multiselect
                opciones = [f"{m['codigo']} - {m['nombre']} ({m['horas_semanales']}h/sem)" for m in materias_semestre]
                
                # Si es edición, preseleccionar las materias que ya tiene el profesor
                default_seleccionadas = []
                if default:
                    for m_prof in default['materias']:
                        for m_malla in materias_semestre:
                            if m_prof['nombre'] == m_malla['nombre']:
                                opcion = f"{m_malla['codigo']} - {m_malla['nombre']} ({m_malla['horas_semanales']}h/sem)"
                                default_seleccionadas.append(opcion)
                
                seleccion = st.multiselect(
                    f"Seleccione materias del semestre {semestre}",
                    opciones,
                    default=default_seleccionadas,
                    key=f"semestre_{semestre}_{nombre if nombre else 'nuevo'}"
                )
                
                # Convertir selección a formato de materias
                for opcion in seleccion:
                    codigo = opcion.split(" - ")[0]
                    materia_malla = utils.buscar_materia_por_codigo(codigo)
                    if materia_malla:
                        materias_seleccionadas.append({
                            "codigo": materia_malla['codigo'],
                            "nombre": materia_malla['nombre'],
                            "semestre": materia_malla['semestre'],
                            "duracion": materia_malla['horas_semanales']
                        })

    # Mostrar resumen de materias seleccionadas
    if materias_seleccionadas:
        st.markdown("### Materias seleccionadas:")
        total_horas = 0
        for materia in materias_seleccionadas:
            st.markdown(f"- **{materia['codigo']}**: {materia['nombre']} ({materia['duracion']}h/sem)")
            total_horas += materia['duracion']
        st.markdown(f"**Total de horas semanales: {total_horas}h**")

    return nombre, horarios, materias_seleccionadas

def gestionar_profesores():
    """
    Muestra y permite gestionar profesores: ver, editar, eliminar, agregar.
    """
    st.markdown("### Gestión de Profesores")
    profesores = utils.cargar_profesores()
    for prof in profesores:
        with st.expander(f"{prof['nombre']}"):
            st.markdown(f"**Horarios disponibles:** {', '.join(prof['horarios_disponibles']) if prof['horarios_disponibles'] else 'Ninguno'}")
            st.markdown("**Materias:**")
            for m in prof['materias']:
                st.markdown(f"- {m['nombre']} (Semestre: {m['semestre']}, Duración: {m['duracion']}h)")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Editar", key=f"editar_{prof['nombre']}"):
                    with st.form(f"form_edit_{prof['nombre']}", clear_on_submit=True):
                        nombre, horarios, materias = formulario_profesor(default=prof)
                        submit = st.form_submit_button("Guardar cambios")
                        if submit:
                            if not nombre or not horarios or any(not m["nombre"] or not m["semestre"] or not m["duracion"] for m in materias):
                                st.warning("Por favor, complete todos los campos antes de guardar.")
                            else:
                                nuevo_prof = {"nombre": nombre, "horarios_disponibles": horarios, "materias": materias}
                                utils.actualizar_profesor(prof['nombre'], nuevo_prof)
                                st.success("Profesor actualizado.")
                                st.experimental_rerun()
            with col2:
                if st.button(f"Eliminar", key=f"eliminar_{prof['nombre']}"):
                    utils.eliminar_profesor(prof['nombre'])
                    st.success("Profesor eliminado.")
                    st.experimental_rerun()
    st.markdown("---")
    st.markdown("#### Agregar nuevo profesor")
    with st.form("form_nuevo_profesor", clear_on_submit=True):
        nombre, horarios, materias = formulario_profesor()
        submit = st.form_submit_button("Agregar profesor")
        if submit:
            if not nombre or not horarios or any(not m["nombre"] or not m["semestre"] or not m["duracion"] for m in materias):
                st.warning("Por favor, complete todos los campos antes de agregar el profesor.")
            else:
                nuevo_prof = {"nombre": nombre, "horarios_disponibles": horarios, "materias": materias}
                utils.guardar_profesores(profesores + [nuevo_prof])
                st.success("Profesor agregado.")
                st.experimental_rerun()

def seleccionar_profesores_para_calculo(profesores):
    """
    Permite seleccionar profesores para el cálculo de horarios.
    Retorna la sublista seleccionada.
    """
    nombres = [p['nombre'] for p in profesores]
    seleccionados = st.multiselect("Seleccione los profesores para el cálculo de horarios", nombres, default=nombres)
    return [p for p in profesores if p['nombre'] in seleccionados]

def gestionar_materias():
    """
    Muestra y permite gestionar materias: ver, editar, eliminar, agregar.
    """
    st.markdown("### Gestión de Materias")
    materias = utils.cargar_materias()
    for mat in materias:
        with st.expander(f"{mat['nombre']}"):
            st.markdown(f"- **Duración:** {mat['duracion']} horas/semana")
            st.markdown(f"- **Semestre:** {mat['semestre']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Editar", key=f"editar_mat_{mat['nombre']}"):
                    with st.form(f"form_edit_mat_{mat['nombre']}", clear_on_submit=True):
                        nombre, duracion, semestre = formulario_materia(default=mat)
                        submit = st.form_submit_button("Guardar cambios")
                        if submit:
                            if not nombre or not duracion or not semestre:
                                st.warning("Por favor, complete todos los campos antes de guardar.")
                            else:
                                nueva_mat = {"nombre": nombre, "duracion": duracion, "semestre": semestre}
                                utils.actualizar_materia(mat['nombre'], nueva_mat)
                                st.success("Materia actualizada.")
                                st.experimental_rerun()
            with col2:
                if st.button(f"Eliminar", key=f"eliminar_mat_{mat['nombre']}"):
                    utils.eliminar_materia(mat['nombre'])
                    st.success("Materia eliminada.")
                    st.experimental_rerun()
    st.markdown("---")
    st.markdown("#### Agregar nueva materia")
    with st.form("form_nueva_materia", clear_on_submit=True):
        nombre, duracion, semestre = formulario_materia()
        submit = st.form_submit_button("Agregar materia")
        if submit:
            if not nombre or not duracion or not semestre:
                st.warning("Por favor, complete todos los campos antes de agregar la materia.")
            else:
                nueva_mat = {"nombre": nombre, "duracion": duracion, "semestre": semestre}
                utils.guardar_materias(materias + [nueva_mat])
                st.success("Materia agregada.")
                st.experimental_rerun()

def gestionar_profesores_dashboard():
    # ... (mantener implementación existente)
    pass

def editar_profesor(prof):
    # ... (mantener implementación existente)
    pass

def gestionar_materias_dashboard():
    # ... (mantener implementación existente)
    pass

def editar_materia(mat):
    # ... (mantener implementación existente)
    pass

def configurar_calculo_horarios_dashboard():
    # ... (mantener implementación existente)
    pass

def gestionar_profesores_con_malla_dashboard():
    """
    Dashboard para gestionar profesores usando la malla curricular.
    """
    st.markdown("#### Profesores (con malla curricular)")
    profesores = utils.cargar_profesores()
    
    # Mostrar profesores existentes
    for prof in profesores:
        tarjeta_profesor(
            prof,
            on_edit=lambda p=prof: editar_profesor_con_malla(p),
            on_delete=lambda p=prof: (utils.eliminar_profesor(p['nombre']), st.experimental_rerun())
        )
    
    # Botón para agregar nuevo profesor
    if st.button("➕ Agregar profesor", key="add_prof_malla"):
        st.session_state['show_prof_malla_form'] = True
    
    # Formulario para nuevo profesor
    if st.session_state.get('show_prof_malla_form'):
        st.markdown("##### Nuevo Profesor (selección desde malla curricular)")
        nombre, horarios, materias = formulario_profesor_con_malla()
        
        if st.button("Guardar profesor", key="save_prof_malla"):
            if not nombre or not horarios or not materias:
                st.warning("Por favor, complete todos los campos y seleccione al menos una materia.")
            else:
                nuevo_prof = {
                    "nombre": nombre, 
                    "horarios_disponibles": horarios, 
                    "materias": materias
                }
                utils.guardar_profesores(profesores + [nuevo_prof])
                st.success("Profesor agregado exitosamente.")
                st.session_state['show_prof_malla_form'] = False
                st.experimental_rerun()

def editar_profesor_con_malla(prof):
    """
    Editar profesor usando la malla curricular.
    """
    st.markdown(f"##### Editar Profesor: {prof['nombre']}")
    nombre, horarios, materias = formulario_profesor_con_malla(default=prof)
    
    if st.button("Guardar cambios", key=f"save_edit_prof_malla_{prof['nombre']}"):
        if not nombre or not horarios or not materias:
            st.warning("Por favor, complete todos los campos y seleccione al menos una materia.")
        else:
            nuevo_prof = {
                "nombre": nombre, 
                "horarios_disponibles": horarios, 
                "materias": materias
            }
            utils.actualizar_profesor(prof['nombre'], nuevo_prof)
            st.success("Profesor actualizado exitosamente.")
            st.experimental_rerun() 