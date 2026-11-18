# Punto de Juego — Academia deportiva

Aplicación académica de gestión deportiva desarrollada con Django 5.2. Permite
inscribir deportistas, elegir disciplina y nivel, administrar membresías y
proteger las funciones con autenticación, permisos y sesiones.

## Contenido

1. [Funcionalidades](#funcionalidades)
2. [Modelo de datos](#modelo-de-datos)
3. [Vistas y rutas](#vistas-y-rutas)
4. [Formularios, validación y seguridad](#formularios-validación-y-seguridad)
5. [Django Admin](#django-admin)
6. [Middleware y sesiones](#middleware-y-sesiones)
7. [Ejecución en Windows](#ejecución-en-windows)
8. [Pruebas y auditoría](#pruebas-y-auditoría)
9. [Evidencias](#evidencias)
10. [Configuración de producción](#configuración-de-producción)

## Funcionalidades

- Registro de cuenta y perfil deportivo.
- Disciplinas: fútbol, básquetbol, vóleibol, natación, atletismo y artes marciales.
- Niveles principiante, intermedio y avanzado.
- Panel personal y edición segura del perfil.
- Consulta de deportistas protegida por permiso.
- Django Admin con búsqueda, filtros, selección de estado y acciones masivas.
- Middleware con identificador de solicitud, registro y cabeceras de seguridad.

## Modelo de datos

El modelo `AthleteProfile` está relacionado uno a uno con el usuario de Django.
Incluye nombre, código de socio, correo, teléfono, disciplina, nivel, fecha de
nacimiento y estado de membresía. La fecha y hora de registro y actualización
se generan automáticamente.

El código de socio tiene el formato `DEP-` seguido de 4 a 8 dígitos. Los
teléfonos aceptan de 7 a 15 dígitos, con prefijo internacional opcional.
La migración `0002_athlete_profiles` transforma el perfil estudiantil anterior
al modelo deportivo y conserva los registros existentes.

## Vistas y rutas

Las rutas de la aplicación están definidas en `core/urls.py` y se incluyen
desde `config/urls.py`. Las rutas de escritura usan POST, formularios validados
y protección CSRF.

| URL | Nombre de ruta / vista | Métodos | Acceso | Plantilla y comportamiento |
|---|---|---|---|---|
| `/` | `home` | GET | Público | `core/home.html`. Muestra la portada y cuenta deportistas y disciplinas con membresía activa. |
| `/registro/` | `register` | GET, POST | Público | `core/register.html`. Usa `AthleteRegistrationForm`; crea usuario y perfil en una transacción, inicia sesión y redirige al panel. |
| `/login/` | `login` (`login_view`) | GET, POST | Público | `core/login.html`. Valida credenciales con `AuthenticationForm`, inicia sesión y redirige al panel. |
| `/logout/` | `logout` (`logout_view`) | POST | Sesión actual | No tiene plantilla. Cierra la sesión, muestra confirmación y redirige al inicio. GET devuelve 405. |
| `/panel/` | `dashboard` | GET | Requiere inicio de sesión | `core/dashboard.html`. Muestra la cuenta y, si existe, el perfil deportivo. |
| `/perfil/editar/` | `edit_profile` | GET, POST | Requiere inicio de sesión | `core/profile.html`. Edita el perfil con `AthleteProfileForm`; si la cuenta no tiene perfil, vuelve al panel con aviso. |
| `/contacto/` | `contact` | GET, POST | Requiere inicio de sesión | `core/contact.html`. Valida un formulario clásico de consulta y muestra confirmación; es demostrativo y no almacena mensajes. |
| `/deportistas/` | `athlete_list` (`AthleteListView`) | GET | Permiso `core.view_athleteprofile` | `core/athlete_list.html`. Lista deportistas paginados, con disciplina, nivel y membresía. Sin permiso, responde 403. |
| `/admin/` | `admin.site.urls` | GET y POST del Admin | Personal administrativo autorizado | Administración nativa de Django para gestionar perfiles y cuentas. |

`@login_required` protege el panel, la edición del perfil y el formulario de
contacto. `AthleteListView` usa `PermissionRequiredMixin`; el acceso se controla
con los permisos de Django. El cierre de sesión solo acepta POST para evitar
que una visita GET cierre la sesión.

## Formularios, validación y seguridad

- `AthleteRegistrationForm` crea la cuenta y su perfil deportivo.
- `AthleteProfileForm` es un `ModelForm` para actualizar el perfil.
- `ContactForm` es un formulario clásico para mostrar el ciclo de validación.
- Las vistas pasan los datos como `Form(request.POST)`, validan con
  `is_valid()` y solo entonces guardan.
- Las plantillas renderizan `form.as_p`, `form.errors` y `{% csrf_token %}`.
- `clean_<campo>()` normaliza y valida datos; `clean()` comprueba que la fecha
  de nacimiento no sea futura y agrega el error al campo con `add_error()`.
- Los validadores regex y restricciones del modelo constituyen validaciones
  adicionales en el servidor y en la base de datos.
- `sanitize_input()` recorta y normaliza espacios; los correos se convierten
  a minúsculas.
- El HTML se escapa al renderizar con el autoescape de Django y el filtro
  `escape`. No se guarda HTML escapado en la base de datos. El ORM parametriza
  las consultas.

## Django Admin

`AthleteProfileAdmin` personaliza:

- `list_display`: socio, nombre, disciplina, nivel, correo, estado, fecha y
  nombre calculado.
- `list_filter` y `search_fields`: filtra por disciplina, nivel, estado y fecha;
  busca por código, nombre, correo o usuario.
- `readonly_fields`: fechas y nombre calculado.
- `fields`: controla expresamente los datos que aparecen en la edición; no
  incluye contraseñas ni campos internos de permisos del usuario.
- `actions`: activa o pausa en lote las membresías seleccionadas.
- `list_select_related`: recupera el usuario relacionado junto con el perfil.

La marca del sitio administrativo está personalizada como **Punto de Juego**.

## Middleware y sesiones

`RequestAuditMiddleware` asigna un identificador por solicitud, devuelve
cabeceras `X-Request-ID`, `X-Content-Type-Options`, `Referrer-Policy` y
`Content-Security-Policy`, y registra método, ruta y estado HTTP. Django agrega
`X-Frame-Options` mediante `XFrameOptionsMiddleware`.

Las sesiones usan el backend de base de datos y expiran a los 30 minutos.
`SESSION_COOKIE_HTTPONLY` y `SameSite=Lax` están habilitados; con `DEBUG=0`,
las cookies de sesión y CSRF se marcan `Secure` y se activa la redirección HTTPS.

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

La aplicación queda en http://127.0.0.1:8000/, el registro en
http://127.0.0.1:8000/registro/ y la administración en
http://127.0.0.1:8000/admin/.

## Pruebas y auditoría

```powershell
py manage.py check
py manage.py test
py manage.py makemigrations --check --dry-run
```

La suite comprueba registro y sesión, acceso protegido, permisos, Admin,
logout, CSRF, cookies seguras, validaciones, escape HTML, cabeceras y logs del
middleware.

## Evidencias

Vista general de la academia: [portada deportiva](evidencias/00-portada.png).

1. **Formularios:** [inscripción deportiva](evidencias/01-formulario-registro.png)
2. **Validación y sanitización:** [errores de campos](evidencias/02-validaciones.png)
3. **Django Admin:** [gestión de deportistas](evidencias/03-django-admin.png)
4. **Sesiones y autenticación:** [panel protegido](evidencias/04-panel-autenticado.png)
5. **Integración y middleware:** [contacto y cabeceras de seguridad](evidencias/05-middleware-formulario.png)

## Configuración de producción

Define `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` y `DJANGO_ALLOWED_HOSTS` desde un
gestor de secretos y ejecuta `py manage.py check --deploy`. No despliegues con
la clave de desarrollo.

Para rotar la clave sin invalidar inmediatamente las firmas existentes, define
la clave nueva en `DJANGO_SECRET_KEY` y pasa temporalmente la anterior en
`DJANGO_SECRET_KEY_FALLBACKS`, separada por comas. Retira la clave anterior
después del periodo de transición.
