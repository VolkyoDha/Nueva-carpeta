"""
Componentes visuales y layout para la app de asignación de horarios universitarios.
Incluye funciones para mostrar títulos y secciones.
"""
import streamlit as st

def mostrar_titulo():
    """Muestra el título principal de la app."""
    st.markdown("<h1 style='text-align:center;'>Asignación de Horarios Universitarios</h1>", unsafe_allow_html=True)

def mostrar_seccion(nombre):
    """Muestra un subtítulo/sección con el nombre dado."""
    st.markdown(f"<h3 style='text-align:center;'>{nombre}</h3>", unsafe_allow_html=True) 