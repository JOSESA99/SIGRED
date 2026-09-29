# Modelo de datos inicial propuesto

Este documento propone un diseño inicial para revisar antes de crear modelos Django o migraciones. El punto de partida recomendado es el inventario compartido, porque respaldos y monitoreo dependen de identificar correctamente unidades, ubicaciones y dispositivos.

## Principios

- El inventario común es la base para los módulos de Santiago y Kevin.
- SIGRED guarda datos operativos propios, trazabilidad, permisos, estados resumidos y referencias externas.
- Oxidized debe conservar la recolección e historial técnico de configuraciones mientras no se decida otra arquitectura.
- Zabbix debe conservar el historial detallado de monitoreo y métricas mientras no se justifique duplicarlo.
- Las credenciales y secretos no deben almacenarse en texto plano.
- Los equipos reales, restauraciones y cambios de configuración requieren autorización de la OTI.
- Las capacidades por dispositivo deben modelarse de forma explícita; no se debe asumir que todos los equipos soportan lo mismo.
- Para SQL Server conviene priorizar campos normalizados, longitudes definidas e índices claros. Usar campos JSON o texto libre solo después de validar soporte y necesidad.

## Módulo compartido: inventario

Responsabilidad: Santiago y Kevin.

### `InstitutionalUnit`

Representa facultades, OTI u otras unidades institucionales.

Campos principales:

- `id`
- `name`
- `code`
- `unit_type`: OTI, facultad, oficina, laboratorio, otro.
- `parent`: relación opcional a otra unidad.
- `is_active`
- `created_at`
- `updated_at`

Restricciones sugeridas:

- `code` único cuando exista.
- `name` obligatorio.

### `Location`

Representa sedes, edificios, pisos, salas, racks u otros puntos físicos.

Campos principales:

- `id`
- `unit`
- `name`
- `location_type`: sede, edificio, piso, ambiente, rack, otro.
- `parent`: relación opcional a otra ubicación.
- `description`
- `is_active`
- `created_at`
- `updated_at`

Relaciones:

- Pertenece a `InstitutionalUnit`.
- Puede tener jerarquía con `parent`.

### `Vendor`

Fabricante del equipo.

Campos principales:

- `id`
- `name`: Cisco, Check Point, otro.
- `website`
- `is_active`

Restricciones sugeridas:

- `name` único.

### `DeviceModel`

Modelo comercial o técnico del equipo.

Campos principales:

- `id`
- `vendor`
- `name`
- `device_family`
- `device_type`: switch, router, firewall, access_point, servidor_red, otro.
- `notes`
- `is_active`

Restricciones sugeridas:

- Único por `vendor` y `name`.

### `Device`

Equipo administrado o inventariado.

Campos principales:

- `id`
- `name`
- `hostname`
- `management_ip`
- `serial_number`
- `asset_code`
- `unit`
- `location`
- `vendor`
- `model`
- `device_type`
- `status`: planned, active, maintenance, retired, unknown.
- `criticality`: low, medium, high, critical.
- `description`
- `is_demo`
- `created_at`
- `updated_at`

Restricciones sugeridas:

- `management_ip` único cuando no sea nulo.
- `serial_number` único cuando no sea nulo.
- `asset_code` único cuando no sea nulo.
- Índices por `unit`, `location`, `status`, `device_type` y `management_ip`.

Notas:

- `is_demo` permite diferenciar datos de desarrollo de inventario real.
- `vendor` y `model` pueden quedar nulos inicialmente si el inventario todavía no está confirmado.

### `DeviceCapability`

Registra capacidades confirmadas por dispositivo o modelo.

Campos principales:

- `id`
- `device`
- `capability`: ssh, telnet, snmp, api, oxidized_backup, zabbix_monitoring, config_restore, interface_metrics, otro.
- `status`: unknown, supported, unsupported, pending_test.
- `source`: manual, detected, imported.
- `notes`
- `verified_at`

Restricciones sugeridas:

- Único por `device` y `capability`.

### `ExternalIdentifier`

Vincula dispositivos SIGRED con sistemas externos.

Campos principales:

- `id`
- `device`
- `system`: oxidized, zabbix, inventario_institucional, otro.
- `external_id`
- `external_name`
- `url`
- `is_active`
- `last_verified_at`

Restricciones sugeridas:

- Único por `system` y `external_id`.
- Único por `device`, `system` y `external_id`.

### `CredentialProfile`

Perfil de credenciales o referencia a un mecanismo seguro.

Campos principales:

- `id`
- `name`
- `purpose`: backup, monitoring, admin, api.
- `auth_type`: ssh_password, ssh_key, snmp_v2, snmp_v3, api_token, otro.
- `storage_reference`
- `is_active`
- `notes`

Notas:

- No guardar contraseñas en texto plano.
- `storage_reference` debe apuntar a una solución segura definida posteriormente.
- La relación con dispositivos puede ser muchos a muchos mediante `DeviceCredentialProfile`.

## Módulo de respaldos y configuraciones

Responsable principal: Santiago.

### `BackupPolicy`

Define reglas de respaldo para un conjunto de dispositivos.

Campos principales:

- `id`
- `name`
- `description`
- `is_active`
- `default_retry_count`
- `default_timeout_seconds`
- `created_by`
- `created_at`
- `updated_at`

### `BackupPolicyDevice`

Asocia políticas con dispositivos.

Campos principales:

- `id`
- `policy`
- `device`
- `enabled`
- `notes`

Restricciones sugeridas:

- Único por `policy` y `device`.

### `BackupSchedule`

Programación de respaldos.

Campos principales:

- `id`
- `policy`
- `frequency`: manual, daily, weekly, monthly, cron.
- `cron_expression`
- `timezone`
- `next_run_at`
- `is_active`

### `BackupRun`

Ejecución manual o programada.

Campos principales:

- `id`
- `policy`
- `triggered_by`
- `trigger_type`: manual, scheduled, retry, external.
- `status`: pending, running, success, partial, failed, canceled.
- `started_at`
- `finished_at`
- `summary`

### `BackupAttempt`

Resultado por dispositivo dentro de una ejecución.

Campos principales:

- `id`
- `run`
- `device`
- `status`: pending, running, success, failed, skipped.
- `attempt_number`
- `started_at`
- `finished_at`
- `error_code`
- `error_message`
- `oxidized_node_ref`
- `oxidized_version_ref`

Notas:

- SIGRED conserva estado, trazabilidad y referencias.
- Oxidized conserva la recolección técnica y el historial de configuración, salvo decisión posterior.

### `ConfigVersion`

Registro SIGRED de una versión conocida de configuración.

Campos principales:

- `id`
- `device`
- `source`: oxidized, manual_import, demo.
- `external_ref`
- `collected_at`
- `checksum`
- `size_bytes`
- `created_by`
- `notes`

Notas:

- No almacenar automáticamente toda la configuración como texto en SQL Server.
- Si luego se requiere guardar contenido, debe justificarse por recuperación, auditoría o disponibilidad local.

### `ConfigComparison`

Comparación entre dos versiones.

Campos principales:

- `id`
- `device`
- `from_version`
- `to_version`
- `change_summary`
- `diff_external_ref`
- `created_by`
- `created_at`

### `RestorePlan`

Preparación de recuperación supervisada.

Campos principales:

- `id`
- `device`
- `config_version`
- `requested_by`
- `approved_by`
- `status`: draft, pending_approval, approved, executed, canceled, rejected.
- `reason`
- `created_at`
- `approved_at`
- `executed_at`

Notas:

- La restauración real requiere coordinación y autorización de la OTI.
- Este modelo prepara y audita el flujo; no implica ejecución automática inicial.

## Módulo de monitoreo e incidentes

Responsable principal: Kevin.

### `MonitoringProfile`

Define cómo se monitorea un dispositivo o grupo.

Campos principales:

- `id`
- `name`
- `description`
- `is_active`
- `zabbix_template_ref`
- `created_at`
- `updated_at`

### `DeviceMonitoring`

Asocia un dispositivo de SIGRED con monitoreo externo.

Campos principales:

- `id`
- `device`
- `profile`
- `enabled`
- `zabbix_host_id`
- `zabbix_host_name`
- `last_sync_at`
- `last_known_availability`

Restricciones sugeridas:

- Único por `device`.
- `zabbix_host_id` único cuando exista.

### `AlertRule`

Regla operativa de alerta visible en SIGRED.

Campos principales:

- `id`
- `name`
- `scope`: device, unit, location, global.
- `severity`: info, warning, average, high, disaster.
- `condition_summary`
- `zabbix_trigger_ref`
- `is_active`

Notas:

- Zabbix mantiene la evaluación técnica de triggers cuando aplique.
- SIGRED conserva la regla de negocio, alcance y trazabilidad local.

### `MonitoringEvent`

Evento relevante recibido o registrado.

Campos principales:

- `id`
- `device`
- `source`: zabbix, manual, system.
- `external_ref`
- `severity`
- `status`: open, acknowledged, resolved, ignored.
- `title`
- `occurred_at`
- `resolved_at`

Notas:

- No duplicar todo el historial de métricas de Zabbix.
- Guardar solo eventos necesarios para flujos de incidentes e indicadores.

### `Incident`

Caso gestionado por SIGRED.

Campos principales:

- `id`
- `code`
- `device`
- `unit`
- `event`
- `title`
- `description`
- `severity`
- `status`: open, acknowledged, assigned, in_progress, resolved, closed, canceled.
- `assigned_to`
- `opened_by`
- `opened_at`
- `acknowledged_at`
- `resolved_at`
- `closed_at`

Restricciones sugeridas:

- `code` único.
- Índices por `status`, `severity`, `assigned_to`, `device` y fechas.

### `IncidentUpdate`

Historial de seguimiento de un incidente.

Campos principales:

- `id`
- `incident`
- `author`
- `update_type`: comment, status_change, assignment, acknowledgement, resolution.
- `message`
- `old_status`
- `new_status`
- `created_at`

### `MaintenanceWindow`

Ventana de mantenimiento para evitar alertas o interpretar eventos.

Campos principales:

- `id`
- `name`
- `scope`: device, unit, location, global.
- `device`
- `unit`
- `location`
- `starts_at`
- `ends_at`
- `reason`
- `created_by`
- `is_active`

### `TopologyLink`

Relación conocida entre equipos o dependencias.

Campos principales:

- `id`
- `source_device`
- `target_device`
- `link_type`: physical, logical, dependency, uplink, unknown.
- `source_interface`
- `target_interface`
- `confidence`: low, medium, high.
- `source`: manual, imported, discovered.
- `is_active`

Notas:

- Crear solo cuando existan datos suficientes.
- Evitar inventar topología antes de confirmar conexiones.

## Módulo compartido: auditoría e integraciones

Responsabilidad: ambos.

### `AuditLog`

Registro de acciones relevantes.

Campos principales:

- `id`
- `actor`
- `action`
- `module`: inventory, backups, monitoring, accounts, integrations.
- `object_type`
- `object_id`
- `summary`
- `created_at`
- `ip_address`

### `IntegrationEndpoint`

Configuración de servicios externos.

Campos principales:

- `id`
- `name`
- `integration_type`: oxidized, zabbix, institutional_inventory, other.
- `base_url`
- `status`: planned, configured, active, disabled, error.
- `last_checked_at`
- `notes`

Notas:

- No guardar secretos directamente.
- Usar referencias seguras para tokens o credenciales.

### `IntegrationSyncLog`

Historial resumido de sincronizaciones.

Campos principales:

- `id`
- `integration`
- `started_at`
- `finished_at`
- `status`: success, partial, failed.
- `records_seen`
- `records_created`
- `records_updated`
- `error_message`

## Qué guarda SIGRED y qué conservan los motores externos

### SIGRED

- Inventario institucional y técnico validado.
- Relaciones entre unidades, ubicaciones y dispositivos.
- Capacidades confirmadas por dispositivo.
- Usuarios, permisos y auditoría.
- Políticas, programación, ejecuciones y resultados de respaldos.
- Referencias a versiones de configuración recolectadas.
- Preparación y aprobación de recuperaciones.
- Vínculos con hosts, nodos, triggers o versiones externas.
- Incidentes, asignaciones, comentarios, estados y cierre.
- Indicadores resumidos cuando sean necesarios para reportes.

### Oxidized

- Conexión técnica a equipos para respaldo de configuraciones.
- Recolección de configuraciones.
- Historial técnico de configuraciones y diferencias, salvo que se decida almacenar una copia parcial o completa en SIGRED con justificación.

### Zabbix

- Recolección de métricas.
- Historial detallado de métricas.
- Evaluación técnica de triggers.
- Disponibilidad y monitoreo de bajo nivel.

## Orden de implementación sugerido

1. Crear app de inventario compartido con unidades, ubicaciones, fabricantes, modelos, dispositivos, capacidades e identificadores externos.
2. Registrar estos modelos en el admin de Django con filtros y búsquedas básicas.
3. Definir grupos/permisos iniciales: administración, inventario, respaldos, monitoreo y consulta.
4. Cargar datos de demostración marcados con `is_demo=True`.
5. Añadir modelos de integración (`IntegrationEndpoint`, `ExternalIdentifier`) sin conectar todavía a servicios reales.
6. Implementar el módulo de respaldos sobre el inventario: políticas, programación, ejecuciones, intentos y referencias a Oxidized.
7. Implementar el módulo de monitoreo sobre el inventario: perfiles, vínculos Zabbix, eventos, incidentes y ventanas de mantenimiento.
8. Construir vistas/API compartidas por dispositivo: inventario, último respaldo, estado de monitoreo e incidentes abiertos.
9. Evaluar la integración real con Oxidized y Zabbix en entorno autorizado por la OTI.
10. Incorporar reportes, indicadores, auditoría ampliada y frontend React/TypeScript.
