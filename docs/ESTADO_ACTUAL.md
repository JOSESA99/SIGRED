# Estado actual comprobado

Fecha de revisión: 2026-09-29.

## Repositorio

- Ruta local: `C:\Users\Santi\Proyectos\SIGRED`.
- Rama actual: `master`.
- Repositorio remoto: `https://github.com/JOSESA99/SIGRED`.
- La rama local sigue a `origin/master`.
- Primer commit publicado: `c1f11b1 chore: initial SIGRED backend setup`.
- No se encontró frontend React/TypeScript en los archivos listados del repositorio.

## Backend Django

Ruta: `C:\Users\Santi\Proyectos\SIGRED\backend`.

Archivos y componentes comprobados:

- Proyecto Django en `backend/config`.
- Aplicación `accounts`.
- Aplicación `inventory` registrada en `INSTALLED_APPS`.
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

También se generó, comprobó y aplicó la migración inicial de inventario:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations inventory
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate inventory
```

Resultado:

- Se creó `inventory/migrations/0001_initial.py`.
- La comprobación posterior devolvió `No changes detected`.
- `mssql-django` 2.0.0 declara soporte para los índices parciales usados por las restricciones únicas opcionales.
- La primera ejecución detectó una condición de índice filtrado incompatible con SQL Server y revirtió la transacción completa.
- Se corrigieron las condiciones para usar `IS NOT NULL` y la segunda ejecución terminó con `Applying inventory.0001_initial... OK`.
- `showmigrations inventory` confirma la migración como aplicada.

La conexión a SQL Server falló dentro del entorno restringido de ejecución, pero funcionó al ejecutar Django con acceso al servicio local. No fue necesario cambiar el `.env`, el controlador ODBC ni las credenciales.

Verificación de migraciones:

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations inventory
```

Resultado: `[X] 0001_initial`.

## Implementado

- Base del proyecto Django.
- Aplicación de usuarios `accounts`.
- Usuario personalizado preparado desde el inicio del proyecto.
- Configuración de SQL Server por variables de entorno.
- Administración de Django habilitada y rotulada para SIGRED.
- Modelos iniciales del inventario compartido: unidades, ubicaciones, fabricantes, modelos, dispositivos, capacidades, identificadores externos y perfiles de credenciales por referencia.
- Administración de inventario con búsquedas, filtros y edición de relaciones.
- Migración inicial de inventario aplicada en SQL Server.

## Falta implementar

- Frontend React con TypeScript.
- Permisos y grupos funcionales del inventario.
- Apps de respaldos/configuraciones y monitoreo/incidentes.
- Integración real con Oxidized.
- Integración real con Zabbix.
- Flujos de auditoría, reportes y paneles.
- Datos de demostración controlados.
- Pruebas automatizadas del dominio.

En esta revisión se crearon las tablas del inventario compartido. No se cargaron datos reales ni de demostración.
