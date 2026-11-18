# Punto de Juego — Academia deportiva

Aplicación académica de gestión deportiva desarrollada con Django 5.2. Permite
inscribir deportistas, elegir disciplina y nivel, administrar membresías y
proteger las funciones con autenticación, permisos y sesiones.

## Funcionalidades

- Registro de cuenta y perfil deportivo con validación en servidor.
- Disciplinas: fútbol, básquetbol, vóleibol, natación, atletismo y artes marciales.
- Niveles principiante, intermedio y avanzado.
- Panel personal y edición segura del perfil.
- Django Admin con búsqueda, filtros, selección de estado y acciones masivas.
- Middleware con identificador de solicitud, registro y cabeceras de seguridad.
- Vistas protegidas por autenticación y permisos; cierre de sesión vía POST/CSRF.

## Formularios y seguridad de entrada

Los formularios POST reciben `Form(request.POST)`, se validan con
`is_valid()` y solo entonces guardan el modelo. Las plantillas muestran
`form.as_p`, errores por campo y el resumen `form.errors`, además del token
CSRF. `clean_<campo>()`, `clean()` y validadores del modelo aplican controles
en campo, formulario y modelo. `sanitize_input()` normaliza espacios y los
correos se convierten a minúsculas. El HTML se escapa al renderizar con el
autoescape de Django y el filtro `escape`; no se guardan etiquetas HTML
escapadas en la base de datos. El ORM parametriza las consultas.

## Ejecución en Windows

Desde PowerShell, en la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Si PowerShell bloquea la activación del entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

La aplicación queda en http://127.0.0.1:8000/ y la administración en
http://127.0.0.1:8000/admin/. Para registrar un deportista, abre
http://127.0.0.1:8000/registro/.

## Comprobaciones

```powershell
py manage.py check
py manage.py test
py manage.py makemigrations --check --dry-run
```

En producción, configura primero las variables de entorno indicadas abajo y
ejecuta también `py manage.py check --deploy`.

## Evidencias de las cinco fases

Vista general de la academia: [portada deportiva](evidencias/00-portada.png).

1. **Formularios:** [inscripción deportiva](evidencias/01-formulario-registro.png)
2. **Validación y sanitización:** [errores de campos](evidencias/02-validaciones.png)
3. **Django Admin:** [gestión de deportistas](evidencias/03-django-admin.png)
4. **Sesiones y autenticación:** [panel protegido](evidencias/04-panel-autenticado.png)
5. **Integración y middleware:** [contacto y cabeceras de seguridad](evidencias/05-middleware-formulario.png)

La configuración de producción usa `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` y
`DJANGO_ALLOWED_HOSTS`. Guarda los valores en un gestor de secretos; no despliegues
con la clave de desarrollo.

Para rotar la clave sin invalidar inmediatamente las firmas existentes, define
la clave nueva en `DJANGO_SECRET_KEY` y pasa temporalmente la anterior en
`DJANGO_SECRET_KEY_FALLBACKS`, separada por comas. Retira la clave anterior
después del periodo de transición.
