Proyecto Integrador de Desarrollo Web - Tech Lab System

Este proyecto es una aplicación web Full Stack para la gestión de equipos de un laboratorio universitario.

Arquitectura:

    Frontend: HTML5, CSS3, JavaScript y Bootstrap.

    Backend: Python con FastAPI y oracledb.

    Base de Datos: Oracle Database Express Edition (XE) corriendo en Docker.

Requisitos previos:

    Python 3.11+

    Docker Desktop

    Git

Instalación y Ejecución:

    Base de datos (Oracle XE):
    Abrir Docker Desktop y ejecutar el contenedor de Oracle:
    docker run -d --name oracle-xe -p 1521:1521 -e ORACLE_PASSWORD=Oracle123 gvenzl/oracle-xe:latest

Luego, ejecutar los scripts SQL en este orden exacto: 01_tables.sql, 02_constraints.sql, 03_data.sql. Además, recordar crear la secuencia con create_seq.sql.

    Backend (FastAPI):
    Abrir una terminal y ejecutar:
    cd backend
    pip install -r requirements.txt
    python -m uvicorn main:app --reload

La documentación de la API estará disponible en http://localhost:8080/docs

    Frontend:
    Abrir una segunda terminal y ejecutar:
    cd frontend
    python -m http.server 5500

Abrir en el navegador: http://localhost:5500/login.html

Credenciales de prueba:

    Admin: admin@lab.edu

    Estudiante: student@lab.edu
    (Para la contraseña, usar el hash bcrypt que está guardado en el archivo 03_data.sql)

Estructura del repositorio:

    /backend: Código fuente de FastAPI (rutas, conexión a Oracle).

    /frontend: Páginas HTML (login, dashboard).

    /docs: Capturas de pantalla y documentación adicional.

    Archivos .sql: Scripts de base de datos.
