# horarios_app

Aplicación en Python con Streamlit para la asignación de horarios universitarios a profesores según materias, disponibilidad y duración semanal.

## Estructura del proyecto

```
horarios_app/
│
├── app.py                      # Archivo principal de Streamlit (flujo general)
├── README.md                   # Documentación general del proyecto
├── requirements.txt            # Lista de dependencias
├── test_materias.py            # Archivo de prueba para el gestor de materias
│
├── data/
│   ├── profesores.json         # Base de datos simple de profesores
│   ├── materias.json           # Información estructurada de las materias
│   └── horarios.json           # Horarios base que se pueden usar
│
├── resources/
│   └── materias.json           # Malla curricular completa con materias del programa
│
├── logic/
│   ├── asignador.py            # Algoritmo principal de asignación con backtracking
│   ├── materias_manager.py     # Gestor CRUD para materias del currículum
│   ├── validaciones.py         # Reglas de negocio y restricciones
│   └── utils.py                # Funciones auxiliares (lectura y escritura de archivos JSON)
│
├── ui/
│   ├── forms.py                # Formularios de entrada de profesores y materias
│   ├── layout.py               # Componentes visuales como títulos, columnas, secciones
│   └── materias_ui.py          # Interfaz de usuario para gestión de materias
│
└── assets/
    └── logo.png                # (Opcional) Recursos gráficos
```

## ¿Cómo correr la app?

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

## Funcionalidades actuales
- Registro de profesores, materias y horarios disponibles.
- Cada materia tiene nombre, semestre y duración semanal.
- Algoritmo de asignación de horarios con backtracking y validaciones.
- Visualización de asignaciones y carga horaria por profesor.
- Mensajes claros de error si no se puede asignar.
- Persistencia automática de datos en archivos JSON.

## Gestión de Materias del Currículum
- **Interfaz completa CRUD**: Agregar, editar, eliminar y visualizar materias
- **Validación de datos**: Verificación automática de campos obligatorios y rangos válidos
- **Malla curricular predefinida**: Archivo `resources/materias.json` con 32 materias del programa de Ingeniería en Sistemas
- **Tabla editable**: Visualización moderna con estadísticas y filtros
- **Persistencia automática**: Cambios guardados inmediatamente en el archivo JSON
- **Validaciones robustas**: 
  - Códigos únicos
  - Semestres entre 1-10
  - Horas semanales y semestrales positivas
  - Campos obligatorios completos

## Escalabilidad
- El código está modularizado para facilitar la edición, eliminación y futuras ampliaciones.
- Separación clara entre lógica, interfaz y datos.
- Arquitectura limpia con clases y funciones bien documentadas. 