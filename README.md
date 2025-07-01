# horarios_app

Aplicación en Python con Streamlit para la asignación de horarios universitarios a profesores según materias, disponibilidad y duración semanal.

## Estructura del proyecto

```
horarios_app/
│
├── app.py                      # Archivo principal de Streamlit (flujo general)
├── README.md                   # Documentación general del proyecto
├── requirements.txt            # Lista de dependencias
│
├── data/
│   ├── profesores.json         # Base de datos simple de profesores
│   ├── materias.json           # Información estructurada de las materias
│   └── horarios.json           # Horarios base que se pueden usar
│
├── logic/
│   ├── asignador.py            # Algoritmo principal de asignación con backtracking
│   ├── validaciones.py         # Reglas de negocio y restricciones
│   └── utils.py                # Funciones auxiliares (lectura y escritura de archivos JSON)
│
├── ui/
│   ├── forms.py                # Formularios de entrada de profesores y materias
│   └── layout.py               # Componentes visuales como títulos, columnas, secciones
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

## Escalabilidad
- El código está modularizado para facilitar la edición, eliminación y futuras ampliaciones.
- Separación clara entre lógica, interfaz y datos. 