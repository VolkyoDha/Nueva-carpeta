"""
app.py - Archivo principal de la aplicación de asignación de horarios universitarios.
Orquesta el flujo general de la app y utiliza componentes de la interfaz modularizados.
"""
import streamlit as st
from ui.forms import formulario_profesor
from ui.layout import mostrar_titulo, mostrar_seccion
from logic.utils import leer_json, escribir_json
from logic.asignador import asignar_horarios

RUTA_PROFESORES = "data/profesores.json"
RUTA_HORARIOS = "data/horarios.json"

def main():
    mostrar_titulo()
    mostrar_seccion("Ingreso de Profesores y Materias")
    profesores = leer_json(RUTA_PROFESORES)
    profesor = formulario_profesor()
    if profesor:
        profesores.append(profesor)
        escribir_json(RUTA_PROFESORES, profesores)
        st.success("Profesor registrado correctamente y guardado en JSON:")
        st.json(profesor)
    # Mostrar todos los profesores registrados
    if profesores:
        st.markdown("### Profesores registrados:")
        for p in profesores:
            st.json(p)
        # Botón para calcular asignaciones
        if st.button("Calcular asignaciones"):
            horarios_base = leer_json(RUTA_HORARIOS)
            asignaciones, errores = asignar_horarios(profesores, horarios_base)
            if asignaciones:
                st.success("Asignaciones realizadas:")
                st.json(asignaciones)
            else:
                st.error("No se pudo asignar horarios:")
                for e in errores:
                    st.markdown(f"- {e}")

if __name__ == "__main__":
    main() 