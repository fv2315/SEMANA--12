# Practica Django - Semana 12

Proyecto académico que integra formularios, validacion, Django Admin, middleware,
sesiones, autenticacion y permisos en Django 5.

## Ejecucion

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Accesos:

- Aplicacion: http://127.0.0.1:8000/
- Registro: http://127.0.0.1:8000/registro/
- Panel: http://127.0.0.1:8000/panel/
- Admin: http://127.0.0.1:8000/admin/

## Evidencias de las cinco fases

1. **Formularios:** [formulario de registro](evidencias/01-formulario-registro.png)
2. **Validacion:** [errores por campo](evidencias/02-validaciones.png)
3. **Django Admin:** [lista de perfiles y acciones](evidencias/03-django-admin.png)
4. **Autenticacion y sesiones:** [panel protegido](evidencias/04-panel-autenticado.png)
5. **Integracion y middleware:** [formulario clasico](evidencias/05-middleware-formulario.png). La respuesta incluye `X-Request-ID`, `X-Content-Type-Options` y `Content-Security-Policy`.

## Validaciones

```powershell
py manage.py check
py manage.py test
py manage.py makemigrations --check
py manage.py migrate
```
