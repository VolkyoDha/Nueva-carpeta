
from typing import Dict, List, Optional, Tuple, Union
import streamlit as st
import pandas as pd
from logic import utils
from logic.asignador import asignar_horarios

# Constantes mejor organizadas
HORARIOS_BASE = [
    "Lunes 7-9", "Lunes 9-11", "Lunes 11-13", "Lunes 13-15",
    "Martes 7-9", "Martes 9-11", "Martes 11-13", "Martes 13-15",
    "Miércoles 7-9", "Miércoles 9-11", "Miércoles 11-13", "Miércoles 13-15",
    "Jueves 7-9", "Jueves 9-11", "Jueves 11-13", "Jueves 13-15",
    "Viernes 7-9", "Viernes 9-11", "Viernes 11-13", "Viernes 13-15"
]

DURACIONES = [1, 2, 4, 6]
MAX_MATERIAS = 10
MAX_SEMESTRES = 12

def _validar_datos_profesor(nombre: str, horarios: List[str], materias: List[Dict]) -> bool:
    """Valida los datos de un profesor antes de guardar."""
    if not nombre.strip():
        st.warning("El nombre del profesor no puede estar vacío.")
        return False
    
    if not horarios:
        st.warning("Debe seleccionar al menos un horario disponible.")
        return False
    
    if not materias:
        st.warning("Debe agregar al menos una materia.")
        return False
    
    for materia in materias:
        if not materia['nombre'].strip():
            st.warning("El nombre de la materia no puede estar vacío.")
            return False
        
        if not (1 <= materia['semestre'] <= MAX_SEMESTRES):
            st.warning(f"El semestre debe estar entre 1 y {MAX_SEMESTRES}.")
            return False
        
        if materia['duracion'] not in DURACIONES:
            st.warning(f"La duración debe ser uno de los valores permitidos: {DURACIONES}.")
            return False
    
    return True

def formulario_profesor(default: Optional[Dict] = None) -> Tuple[str, List[str], List[Dict]]:
    """
    Formulario para ingresar o editar un profesor y sus materias.
    
    Args:
        default: Diccionario con datos del profesor para edición (opcional)
        
    Returns:
        Tuple con (nombre, horarios_disponibles, lista_de_materias)
    """
    # Configuración inicial basada en si es edición o creación
    es_edicion = default is not None
    key_suffix = f"_edit_{default['nombre']}" if es_edicion else ""
    
    # Sección de datos básicos del profesor
    nombre = st.text_input(
        "Nombre del profesor", 
        value=default['nombre'] if es_edicion else "",
        key=f"nombre{key_suffix}"
    )
    
    horarios = st.multiselect(
        "Horarios disponibles", 
        HORARIOS_BASE,
        default=default['horarios_disponibles'] if es_edicion else [],
        key=f"horarios{key_suffix}"
    )
    
    # Sección de materias
    st.subheader("Materias que dicta")
    n_materias = st.slider(
        "¿Cuántas materias dicta?", 
        min_value=1, 
        max_value=MAX_MATERIAS, 
        value=len(default['materias']) if es_edicion else 1,
        key=f"n_materias{key_suffix}"
    )
    
    # Preparar valores por defecto para materias
    materias_default = (
        default['materias'][:n_materias] + 
        [{} for _ in range(n_materias - len(default['materias']))] 
        if es_edicion else 
        [{} for _ in range(n_materias)]
    )
    
    materias = []
    for i in range(n_materias):
        with st.container():
            st.markdown(f"### Materia #{i+1}")
            
            nombre_mat = st.text_input(
                f"Nombre", 
                value=materias_default[i].get('nombre', ''),
                key=f"mat_nombre{key_suffix}_{i}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                semestre = st.number_input(
                    f"Semestre", 
                    min_value=1, 
                    max_value=MAX_SEMESTRES, 
                    value=materias_default[i].get('semestre', 1),
                    key=f"mat_sem{key_suffix}_{i}"
                )
            with col2:
                duracion = st.selectbox(
                    f"Duración semanal (horas)", 
                    DURACIONES,
                    index=DURACIONES.index(materias_default[i].get('duracion', 1)) 
                    if materias_default[i].get('duracion') in DURACIONES else 0,
                    key=f"mat_dur{key_suffix}_{i}"
                )
            
            materias.append({
                "nombre": nombre_mat, 
                "semestre": semestre, 
                "duracion": duracion
            })
    
    return nombre, horarios, materias

def formulario_materia(default: Optional[Dict] = None) -> Tuple[str, int, int]:
    """
    Formulario para ingresar o editar una materia.
    
    Args:
        default: Diccionario con datos de la materia para edición (opcional)
        
    Returns:
        Tuple con (nombre, duracion, semestre)
    """
    es_edicion = default is not None
    key_suffix = f"_edit_{default['nombre']}" if es_edicion else ""
    
    nombre = st.text_input(
        "Nombre de la materia", 
        value=default['nombre'] if es_edicion else "",
        key=f"mat_nombre{key_suffix}"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        duracion = st.selectbox(
            "Duración semanal (horas)", 
            DURACIONES,
            index=DURACIONES.index(default['duracion']) if es_edicion and default['duracion'] in DURACIONES else 0,
            key=f"mat_dur{key_suffix}"
        )
    with col2:
        semestre = st.number_input(
            "Semestre", 
            min_value=1, 
            max_value=MAX_SEMESTRES, 
            value=default['semestre'] if es_edicion else 1,
            key=f"mat_sem{key_suffix}"
        )
    
    return nombre, duracion, semestre

def formulario_profesor_con_malla(default: Optional[Dict] = None) -> Tuple[str, List[str], List[Dict]]:
    """
    Formulario para registrar profesor seleccionando materias desde la malla curricular.
    
    Args:
        default: Diccionario con datos del profesor para edición (opcional)
        
    Returns:
        Tuple con (nombre, horarios_disponibles, lista_de_materias)
    """
    try:
        malla = utils.cargar_malla_curricular()
        if not malla:
            st.error("No se pudo cargar la malla curricular. Verifique que exista.")
            return None, None, None
    except Exception as e:
        st.error(f"Error al cargar la malla curricular: {str(e)}")
        return None, None, None
    
    es_edicion = default is not None
    key_suffix = f"_edit_{default['nombre']}" if es_edicion else ""
    
    # Sección de datos básicos
    st.subheader("Datos del profesor")
    nombre = st.text_input(
        "Nombre del profesor", 
        value=default['nombre'] if es_edicion else "",
        key=f"nombre_malla{key_suffix}"
    )
    
    horarios = st.multiselect(
        "Horarios disponibles", 
        HORARIOS_BASE,
        default=default['horarios_disponibles'] if es_edicion else [],
        key=f"horarios_malla{key_suffix}"
    )
    
    # Sección de selección de materias
    st.subheader("Selección de materias desde malla curricular")
    
    # Obtener semestres únicos ordenados
    semestres = sorted({m['semestre'] for m in malla})
    
    materias_seleccionadas = []
    total_horas = 0
    
    for semestre in semestres:
        with st.expander(f"Semestre {semestre}"):
            materias_semestre = utils.obtener_materias_por_semestre(semestre)
            
            if not materias_semestre:
                st.warning(f"No hay materias registradas para el semestre {semestre}")
                continue
                
            # Preparar opciones y valores por defecto
            opciones = [
                f"{m['codigo']} - {m['nombre']} ({m['horas_semanales']}h/sem)" 
                for m in materias_semestre
            ]
            
            default_seleccionadas = []
            if es_edicion:
                for m_prof in default['materias']:
                    for m_malla in materias_semestre:
                        if m_prof['nombre'] == m_malla['nombre']:
                            opcion = f"{m_malla['codigo']} - {m_malla['nombre']} ({m_malla['horas_semanales']}h/sem)"
                            default_seleccionadas.append(opcion)
            
            seleccion = st.multiselect(
                f"Materias del semestre {semestre}",
                opciones,
                default=default_seleccionadas,
                key=f"semestre_{semestre}{key_suffix}"
            )
            
            # Procesar selección
            for opcion in seleccion:
                try:
                    codigo = opcion.split(" - ")[0]
                    materia_malla = utils.buscar_materia_por_codigo(codigo)
                    
                    if materia_malla:
                        materias_seleccionadas.append({
                            "codigo": materia_malla['codigo'],
                            "nombre": materia_malla['nombre'],
                            "semestre": materia_malla['semestre'],
                            "duracion": materia_malla['horas_semanales']
                        })
                        total_horas += materia_malla['horas_semanales']
                except Exception as e:
                    st.error(f"Error al procesar materia {opcion}: {str(e)}")
    
    # Mostrar resumen
    if materias_seleccionadas:
        st.subheader("Resumen de materias seleccionadas")
        
        df = pd.DataFrame(materias_seleccionadas)
        st.dataframe(df[['codigo', 'nombre', 'semestre', 'duracion']].rename(
            columns={'duracion': 'horas/semana'}), 
            hide_index=True
        )
        
        st.markdown(f"**Total de horas semanales: {total_horas}h**")
    
    return nombre, horarios, materias_seleccionadas

def gestionar_profesores() -> None:
    """Interfaz completa para gestionar profesores."""
    try:
        profesores = utils.cargar_profesores()
    except Exception as e:
        st.error(f"Error al cargar profesores: {str(e)}")
        return
    
    st.title("Gestión de Profesores")
    
    # Listado de profesores existentes
    st.header("Profesores registrados")
    
    if not profesores:
        st.info("No hay profesores registrados aún.")
    else:
        for i, prof in enumerate(profesores):
            with st.expander(f"{prof['nombre']} ({len(prof['materias'])} materias)"):
                # Mostrar información del profesor
                st.markdown(f"**Horarios disponibles:** {', '.join(prof['horarios_disponibles']) or 'Ninguno'}")
                
                st.markdown("**Materias que dicta:**")
                for m in prof['materias']:
                    st.markdown(f"- {m['nombre']} (Semestre: {m['semestre']}, Duración: {m['duracion']}h/sem)")
                
                # Botones de acción
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("Editar", key=f"editar_{i}"):
                        st.session_state['editar_profesor'] = i
                
                with col2:
                    if st.button("Eliminar", key=f"eliminar_{i}"):
                        try:
                            utils.eliminar_profesor(prof['nombre'])
                            st.success("Profesor eliminado correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar profesor: {str(e)}")
                
                with col3:
                    if st.button("Usar malla curricular", key=f"malla_{i}"):
                        st.session_state['editar_profesor_malla'] = i
    
    # Formulario de edición (normal)
    if 'editar_profesor' in st.session_state:
        st.header("Editar profesor")
        prof = profesores[st.session_state['editar_profesor']]
        
        with st.form(f"form_editar_{prof['nombre']}"):
            nombre, horarios, materias = formulario_profesor(default=prof)
            
            if st.form_submit_button("Guardar cambios"):
                if _validar_datos_profesor(nombre, horarios, materias):
                    try:
                        nuevo_prof = {
                            "nombre": nombre,
                            "horarios_disponibles": horarios,
                            "materias": materias
                        }
                        utils.actualizar_profesor(prof['nombre'], nuevo_prof)
                        st.success("Profesor actualizado correctamente.")
                        del st.session_state['editar_profesor']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar profesor: {str(e)}")
        
        if st.button("Cancelar"):
            del st.session_state['editar_profesor']
    
    # Formulario de edición con malla
    if 'editar_profesor_malla' in st.session_state:
        st.header("Editar profesor (con malla curricular)")
        prof = profesores[st.session_state['editar_profesor_malla']]
        
        nombre, horarios, materias = formulario_profesor_con_malla(default=prof)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Guardar cambios"):
                if _validar_datos_profesor(nombre, horarios, materias):
                    try:
                        nuevo_prof = {
                            "nombre": nombre,
                            "horarios_disponibles": horarios,
                            "materias": materias
                        }
                        utils.actualizar_profesor(prof['nombre'], nuevo_prof)
                        st.success("Profesor actualizado correctamente.")
                        del st.session_state['editar_profesor_malla']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar profesor: {str(e)}")
        with col2:
            if st.button("Cancelar"):
                del st.session_state['editar_profesor_malla']
    
    # Formulario para nuevo profesor
    st.header("Agregar nuevo profesor")
    
    tab1, tab2 = st.tabs(["Formulario manual", "Desde malla curricular"])
    
    with tab1:
        with st.form("form_nuevo_profesor"):
            nombre, horarios, materias = formulario_profesor()
            
            if st.form_submit_button("Agregar profesor"):
                if _validar_datos_profesor(nombre, horarios, materias):
                    try:
                        nuevo_prof = {
                            "nombre": nombre,
                            "horarios_disponibles": horarios,
                            "materias": materias
                        }
                        utils.guardar_profesores(profesores + [nuevo_prof])
                        st.success("Profesor agregado correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al agregar profesor: {str(e)}")
    
    with tab2:
        nombre, horarios, materias = formulario_profesor_con_malla()
        
        if st.button("Agregar profesor (malla)"):
            if _validar_datos_profesor(nombre, horarios, materias):
                try:
                    nuevo_prof = {
                        "nombre": nombre,
                        "horarios_disponibles": horarios,
                        "materias": materias
                    }
                    utils.guardar_profesores(profesores + [nuevo_prof])
                    st.success("Profesor agregado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al agregar profesor: {str(e)}")

def gestionar_materias() -> None:
    """Interfaz completa para gestionar materias."""
    try:
        materias = utils.cargar_materias()
    except Exception as e:
        st.error(f"Error al cargar materias: {str(e)}")
        return
    
    st.title("Gestión de Materias")
    
    # Listado de materias existentes
    st.header("Materias registradas")
    
    if not materias:
        st.info("No hay materias registradas aún.")
    else:
        for i, mat in enumerate(materias):
            with st.expander(f"{mat['nombre']}"):
                st.markdown(f"**Semestre:** {mat['semestre']}")
                st.markdown(f"**Duración:** {mat['duracion']} horas/semana")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Editar", key=f"editar_mat_{i}"):
                        st.session_state['editar_materia'] = i
                
                with col2:
                    if st.button("Eliminar", key=f"eliminar_mat_{i}"):
                        try:
                            utils.eliminar_materia(mat['nombre'])
                            st.success("Materia eliminada correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar materia: {str(e)}")
    
    # Formulario de edición
    if 'editar_materia' in st.session_state:
        st.header("Editar materia")
        mat = materias[st.session_state['editar_materia']]
        
        with st.form(f"form_editar_mat_{mat['nombre']}"):
            nombre, duracion, semestre = formulario_materia(default=mat)
            
            if st.form_submit_button("Guardar cambios"):
                if not nombre.strip():
                    st.warning("El nombre de la materia no puede estar vacío.")
                else:
                    try:
                        nueva_mat = {
                            "nombre": nombre,
                            "duracion": duracion,
                            "semestre": semestre
                        }
                        utils.actualizar_materia(mat['nombre'], nueva_mat)
                        st.success("Materia actualizada correctamente.")
                        del st.session_state['editar_materia']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar materia: {str(e)}")
        
        if st.button("Cancelar"):
            del st.session_state['editar_materia']
    
    # Formulario para nueva materia
    st.header("Agregar nueva materia")
    
    with st.form("form_nueva_materia"):
        nombre, duracion, semestre = formulario_materia()
        
        if st.form_submit_button("Agregar materia"):
            if not nombre.strip():
                st.warning("El nombre de la materia no puede estar vacío.")
            else:
                try:
                    nueva_mat = {
                        "nombre": nombre,
                        "duracion": duracion,
                        "semestre": semestre
                    }
                    utils.guardar_materias(materias + [nueva_mat])
                    st.success("Materia agregada correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al agregar materia: {str(e)}")

def seleccionar_profesores_para_calculo(profesores: List[Dict]) -> List[Dict]:
    """
    Permite seleccionar profesores para el cálculo de horarios.
    
    Args:
        profesores: Lista completa de profesores
        
    Returns:
        Lista de profesores seleccionados
    """
    st.subheader("Selección de profesores para asignación")
    
    if not profesores:
        st.warning("No hay profesores registrados.")
        return []
    
    nombres = [p['nombre'] for p in profesores]
    seleccionados = st.multiselect(
        "Seleccione los profesores para el cálculo", 
        nombres,
        default=nombres,
        key="seleccion_profesores"
    )
    
    return [p for p in profesores if p['nombre'] in seleccionados]

# Funciones de dashboard (simplificadas para el ejemplo)
def gestionar_profesores_dashboard():
    """Versión simplificada para dashboard."""
    gestionar_profesores()

def gestionar_materias_dashboard():
    """Versión simplificada para dashboard."""
    gestionar_materias()

def configurar_calculo_horarios_dashboard():
    """Configuración para dashboard."""
    profesores = utils.cargar_profesores()
    return seleccionar_profesores_para_calculo(profesores)