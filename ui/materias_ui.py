"""
Módulo de interfaz de usuario para gestionar materias.
Proporciona formularios y tablas para operaciones CRUD de materias.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from logic.materias_manager import MateriasManager


def render_materias_section():
    """
    Renderiza la sección completa de gestión de materias.
    Incluye tabla, formularios de agregar/editar y funcionalidad de eliminación.
    """
    st.header("📚 Gestión de Materias")
    st.markdown("---")
    
    # Inicializar el gestor de materias
    materias_manager = MateriasManager()
    
    # Cargar materias actuales
    materias = materias_manager.load_materias()
    
    # Crear dos columnas: tabla y formularios
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_materias_table(materias, materias_manager)
    
    with col2:
        render_materias_forms(materias_manager)


def render_materias_table(materias: List[Dict], materias_manager: MateriasManager):
    """
    Renderiza la tabla de materias con funcionalidad de edición y eliminación.
    
    Args:
        materias: Lista de materias a mostrar
        materias_manager: Instancia del gestor de materias
    """
    st.subheader("📋 Lista de Materias")
    
    if not materias:
        st.info("No hay materias registradas. Agrega una nueva materia usando el formulario.")
        return
    
    # Convertir a DataFrame para mejor visualización
    df = pd.DataFrame(materias)
    
    # Reordenar columnas para mejor visualización
    column_order = ['codigo', 'nombre', 'semestre', 'horas_semanales', 'horas_semestrales']
    df = df[column_order]
    
    # Renombrar columnas para mejor presentación
    df_renamed = df.rename(columns={
        'codigo': 'Código',
        'nombre': 'Nombre',
        'semestre': 'Semestre',
        'horas_semanales': 'Horas Semanales',
        'horas_semestrales': 'Horas Semestrales'
    })
    
    # Mostrar tabla con opciones de edición
    st.dataframe(
        df_renamed,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Código": st.column_config.TextColumn("Código", width="medium"),
            "Nombre": st.column_config.TextColumn("Nombre", width="large"),
            "Semestre": st.column_config.NumberColumn("Semestre", width="small"),
            "Horas Semanales": st.column_config.NumberColumn("Horas Semanales", width="small"),
            "Horas Semestrales": st.column_config.NumberColumn("Horas Semestrales", width="small")
        }
    )
    
    # Estadísticas
    st.markdown("---")
    st.metric("Total Materias", len(materias))
    semestres_unicos = len(set(m['semestre'] for m in materias))
    st.metric("Semestres", semestres_unicos)
    total_horas = sum(m['horas_semanales'] for m in materias)
    st.metric("Total Horas Semanales", total_horas)
    
    # Funcionalidad de edición y eliminación
    render_edit_delete_controls(materias, materias_manager)


def render_edit_delete_controls(materias: List[Dict], materias_manager: MateriasManager):
    """
    Renderiza los controles para editar y eliminar materias.
    
    Args:
        materias: Lista de materias
        materias_manager: Instancia del gestor de materias
    """
    st.markdown("---")
    st.subheader("✏️ Editar/Eliminar Materia")
    
    # Selector de materia para editar/eliminar
    codigos = [m['codigo'] for m in materias]
    codigos_nombres = [f"{m['codigo']} - {m['nombre']}" for m in materias]
    
    if codigos:
        materia_seleccionada = st.selectbox(
            "Selecciona una materia:",
            options=codigos_nombres,
            key="materia_selector"
        )
        
        if materia_seleccionada:
            codigo_seleccionado = materia_seleccionada.split(" - ")[0]
            materia = materias_manager.get_materia_by_codigo(codigo_seleccionado)
            
            if materia:
                # Mostrar datos actuales
                st.markdown("**Datos actuales:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Código:** {materia['codigo']}")
                    st.write(f"**Nombre:** {materia['nombre']}")
                    st.write(f"**Semestre:** {materia['semestre']}")
                
                with col2:
                    st.write(f"**Horas Semanales:** {materia['horas_semanales']}")
                    st.write(f"**Horas Semestrales:** {materia['horas_semestrales']}")
                
                # Botones de acción
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("✏️ Editar", key="btn_edit_materia"):
                        st.session_state.editing_materia = materia
                        st.session_state.show_edit_form = True
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Eliminar", key="btn_delete_materia", type="secondary"):
                        success, message = materias_manager.delete_materia(codigo_seleccionado)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)


def render_materias_forms(materias_manager: MateriasManager):
    """
    Renderiza los formularios para agregar y editar materias.
    
    Args:
        materias_manager: Instancia del gestor de materias
    """
    # Inicializar variables de sesión
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'editing_materia' not in st.session_state:
        st.session_state.editing_materia = None
    
    # Formulario de edición
    if st.session_state.show_edit_form and st.session_state.editing_materia:
        render_edit_materia_form(materias_manager)
    
    # Formulario de agregar nueva materia
    else:
        render_add_materia_form(materias_manager)


def render_add_materia_form(materias_manager: MateriasManager):
    """
    Renderiza el formulario para agregar una nueva materia.
    
    Args:
        materias_manager: Instancia del gestor de materias
    """
    st.subheader("➕ Agregar Nueva Materia")
    
    with st.form("add_materia_form", clear_on_submit=True):
        # Campos del formulario
        codigo = st.text_input("Código de la materia:", placeholder="Ej: TIP01BFT01")
        nombre = st.text_input("Nombre de la materia:", placeholder="Ej: FUNDAMENTOS DE MATEMÁTICA")
        
        col1, col2 = st.columns(2)
        with col1:
            semestre = st.number_input("Semestre:", min_value=1, max_value=10, value=1, step=1)
            horas_semanales = st.number_input("Horas Semanales:", min_value=1, max_value=20, value=4, step=1)
        
        with col2:
            horas_semestrales = st.number_input("Horas Semestrales:", min_value=1, max_value=200, value=64, step=1)
        
        # Botón de envío
        submitted = st.form_submit_button("➕ Agregar Materia", type="primary")
        
        if submitted:
            # Crear diccionario con los datos
            nueva_materia = {
                'codigo': codigo.strip(),
                'nombre': nombre.strip(),
                'semestre': semestre,
                'horas_semanales': horas_semanales,
                'horas_semestrales': horas_semestrales
            }
            
            # Validar y agregar
            success, message = materias_manager.add_materia(nueva_materia)
            
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def render_edit_materia_form(materias_manager: MateriasManager):
    """
    Renderiza el formulario para editar una materia existente.
    
    Args:
        materias_manager: Instancia del gestor de materias
    """
    st.subheader("✏️ Editar Materia")
    
    materia = st.session_state.editing_materia
    
    with st.form("edit_materia_form"):
        # Campos del formulario con valores actuales
        codigo = st.text_input("Código de la materia:", value=materia['codigo'])
        nombre = st.text_input("Nombre de la materia:", value=materia['nombre'])
        
        col1, col2 = st.columns(2)
        with col1:
            semestre = st.number_input("Semestre:", min_value=1, max_value=10, value=materia['semestre'], step=1)
            horas_semanales = st.number_input("Horas Semanales:", min_value=1, max_value=20, value=materia['horas_semanales'], step=1)
        
        with col2:
            horas_semestrales = st.number_input("Horas Semestrales:", min_value=1, max_value=200, value=materia['horas_semestrales'], step=1)
        
        # Botones de acción
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancelar"):
                st.session_state.show_edit_form = False
                st.session_state.editing_materia = None
                st.rerun()
        
        if submitted:
            # Crear diccionario con los datos actualizados
            materia_actualizada = {
                'codigo': codigo.strip(),
                'nombre': nombre.strip(),
                'semestre': semestre,
                'horas_semanales': horas_semanales,
                'horas_semestrales': horas_semestrales
            }
            
            # Validar y actualizar
            success, message = materias_manager.update_materia(materia['codigo'], materia_actualizada)
            
            if success:
                st.success(message)
                st.session_state.show_edit_form = False
                st.session_state.editing_materia = None
                st.rerun()
            else:
                st.error(message)


def render_materias_filter_section():
    """
    Renderiza una sección de filtros para las materias.
    Útil para buscar y filtrar materias por semestre.
    """
    st.subheader("🔍 Filtros")
    
    materias_manager = MateriasManager()
    materias = materias_manager.load_materias()
    
    if not materias:
        st.info("No hay materias para filtrar.")
        return
    
    # Filtro por semestre
    semestres_disponibles = sorted(list(set(m['semestre'] for m in materias)))
    semestre_filtro = st.selectbox(
        "Filtrar por semestre:",
        options=["Todos"] + semestres_disponibles,
        key="semestre_filter"
    )
    
    # Aplicar filtro
    if semestre_filtro != "Todos":
        materias_filtradas = [m for m in materias if m['semestre'] == semestre_filtro]
    else:
        materias_filtradas = materias
    
    # Mostrar materias filtradas
    if materias_filtradas:
        st.markdown(f"**Materias del semestre {semestre_filtro}:**")
        df_filtrado = pd.DataFrame(materias_filtradas)
        st.dataframe(
            df_filtrado[['codigo', 'nombre', 'horas_semanales', 'horas_semestrales']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(f"No hay materias en el semestre {semestre_filtro}.") 