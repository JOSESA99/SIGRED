# Estado actual comprobado

Fecha de revisión: 2026-09-29.

## Repositorio

- Ruta local: `C:\Users\Santi\Proyectos\SIGRED`.
- Rama actual: `master`.
- Git reporta que todavía no hay commits.
- El directorio `backend/` está sin seguimiento en Git.
- No se encontró frontend React/TypeScript en los archivos listados del repositorio.
- No existían documentos del proyecto en la raíz antes de esta revisión.

## Backend Django

Ruta: `C:\Users\Santi\Proyectos\SIGRED\backend`.

Archivos y componentes comprobados:

- Proyecto Django en `backend/config`.
- Aplicación `accounts`.
- Modelo personalizado `accounts.User` basado en `AbstractUser`.
- `AUTH_USER_MODEL = "accounts.User"` configurado en `config/settings.py`.
- `accounts` registrado en `INSTALLED_APPS`.
- Administración de Django en `config/urls.py` bajo `admin/`.
- Administración personalizada con textos de SIGRED en `accounts/admin.py`.
- Migración inicial de `accounts` existente en `accounts/migrations/0001_initial.py`.
- `.gitignore` ignora `.venv/`, `.env`, `__pycache__/`, `*.pyc` y `db.sqlite3`.
- Existe un archivo `db.sqlite3` vacío, pero la configuración activa revisada usa SQL Server mediante `ENGINE = "mssql"`.

## Configuración y base de datos

Según `config/settings.py`:

- Se carga `backend/.env` con `python-dotenv`.
- `SECRET_KEY`, credenciales de base de datos y driver ODBC se leen desde variables de entorno.
- La base configurada usa `mssql-django`.
- El driver se lee desde `DB_DRIVER`.
- La conexión local usa `Encrypt=yes;TrustServerCertificate=yes`.
- `LANGUAGE_CODE = "es"`.
- `TIME_ZONE = "America/Lima"`.

No se leyó ni copió el contenido de `backend/.env` para evitar exponer secretos.

## Verificaciones ejecutadas

Comando ejecutado desde `backend/`:

```powershell
.\.venv\Scripts\python.exe manage.py check
```

Resultado:

- `System check identified no issues (0 silenced).`

También se intentó una verificación de migraciones de solo lectura:

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations
```

Resultado de esta sesión:

- Falló al conectar con SQL Server mediante ODBC Driver 18.
- El error reportó problemas relacionados con cifrado/SSL y conexión a `DESKTOP-U3SQL29\SQL2025EDE`.

Este fallo describe el estado observado en esta ejecución. El contexto recibido indica que anteriormente la conexión desde Django ya fue comprobada con `SELECT DB_NAME()` y devolvió `SIGRED`, y que las migraciones de `accounts`, `auth`, `admin`, `contenttypes` y `sessions` fueron aplicadas. Para continuar con cambios de base de datos será necesario confirmar nuevamente la conectividad local.

## Implementado

- Base del proyecto Django.
- Aplicación de usuarios `accounts`.
- Usuario personalizado preparado desde el inicio del proyecto.
- Configuración de SQL Server por variables de entorno.
- Administración de Django habilitada y rotulada para SIGRED.

## Falta implementar

- Frontend React con TypeScript.
- Apps de dominio para inventario, respaldos/configuraciones y monitoreo/incidentes.
- Modelos, migraciones, administración y permisos de inventario.
- Integración real con Oxidized.
- Integración real con Zabbix.
- Flujos de auditoría, reportes y paneles.
- Datos de demostración controlados.
- Pruebas automatizadas del dominio.

En esta revisión no se crearon tablas de dominio ni se ejecutaron migraciones nuevas.
