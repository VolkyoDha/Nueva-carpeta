"""
app.py - Programa para calcular horarios
Universidad Central del Ecuador
Interfaz moderna, modular y clara usando Streamlit.
"""
import streamlit as st
import pandas as pd
import os
from ui.forms import (
    formulario_profesor, formulario_materia,
    gestionar_profesores, gestionar_materias,
    seleccionar_profesores_para_calculo
)
from ui.layout import mostrar_titulo
from ui.materias_ui import render_materias_section
from logic.utils import cargar_profesores, cargar_materias, leer_json
from logic.asignador import asignar_horarios

RUTA_LOGO = "assets/logo.png"
RUTA_HORARIOS = "data/horarios.json"

# ------------------- Layout principal -------------------
def main():
    st.set_page_config(page_title="Programa para calcular horarios", layout="wide")
    # Encabezado y logo
    mostrar_titulo("Programa para calcular horarios")
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, width=180)
    st.markdown("---")

    # Layout con columnas: menú a la derecha
    col1, col2 = st.columns([3, 1])
    with col2:
        menu = st.radio(
            "Menú",
            ["Gestión de Profesores", "Gestión de Materias", "Configuración de Horarios"],
            index=0
        )
    with col1:
        if menu == "Gestión de Profesores":
            st.subheader("Profesores registrados")
            profesores = cargar_profesores()
            if profesores:
                df = pd.DataFrame(profesores)
                st.dataframe(df[["nombre", "horarios_disponibles", "materias"]], use_container_width=True, hide_index=True)
            else:
                st.info("No hay profesores registrados.")
            st.markdown("---")
            gestionar_profesores()

        elif menu == "Gestión de Materias":
            # Usar la nueva interfaz de gestión de materias
            render_materias_section()

        elif menu == "Configuración de Horarios":
            st.subheader("Configuración y cálculo de horarios")
            profesores = cargar_profesores()
            if not profesores:
                st.info("Debe registrar al menos un profesor para calcular horarios.")
            else:
                seleccionados = seleccionar_profesores_para_calculo(profesores)
                if seleccionados and st.button("Calcular horarios", type="primary"):
                    horarios_base = leer_json(RUTA_HORARIOS)
                    asignaciones, errores = asignar_horarios(seleccionados, horarios_base)
                    if asignaciones:
                        st.success("Asignaciones realizadas:")
                        st.dataframe(pd.DataFrame(asignaciones), use_container_width=True, hide_index=True)
                        # Carga horaria por profesor
                        st.markdown("#### Carga horaria por profesor")
                        df = pd.DataFrame(asignaciones)
                        resumen = df.groupby('profesor').agg(
                            bloques=('horario', 'count'),
                        ).reset_index()
                        resumen['horas'] = resumen['bloques'] * 2
                        st.dataframe(resumen, use_container_width=True, hide_index=True)
                    else:
                        st.error("No se pudo asignar horarios:")
                        for e in errores:
                            st.markdown(f"- {e}")

if __name__ == "__main__":
    main() 