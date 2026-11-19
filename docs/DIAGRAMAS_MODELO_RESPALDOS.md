# Diagramas del modelo de políticas y respaldos

Estos diagramas describen las relaciones observadas en los modelos Django actuales. No representan una propuesta de migración.

![Diagrama entidad-relación del módulo de respaldos](./diagrama-modelo-respaldos.svg)

## Diagrama entidad-relación

El SVG muestra las entidades centrales y una selección de campos para que sea legible. Las entidades `User`, `ExternalIdentifier` y `ConfigComparison` también tienen relaciones con estos modelos y se detallan en el diagrama Mermaid siguiente.

La relación entre `BackupAttempt.oxidized_version_ref` y `ConfigVersion.external_ref` es una referencia textual, no una clave foránea. `BackupSchedule` tampoco tiene una relación directa con `BackupRun`; una ejecución registra la política y el tipo de disparador, pero no cuál programación la originó.

<!-- mermaid-checked: every attribute is `<type> <name> [<key>] ["<description>"]` with at most one of PK/FK/UK, no \n in descriptions, no {} in descriptions, every relationship label is double-quoted -->
```mermaid
erDiagram
    User ||--o{ BackupPolicy : "creates"
    User o|--o{ BackupRun : "triggers"
    User o|--o{ ConfigVersion : "registers"
    User ||--o{ ConfigComparison : "creates"
    BackupPolicy ||--o{ BackupPolicyDevice : "assigns devices"
    Device ||--o{ BackupPolicyDevice : "is assigned"
    BackupPolicy ||--o{ BackupSchedule : "has schedules"
    BackupPolicy ||--o{ BackupRun : "groups runs"
    BackupRun ||--o{ BackupAttempt : "contains attempts"
    Device ||--o{ BackupAttempt : "is attempted"
    Device ||--o{ ConfigVersion : "has versions"
    Device ||--o{ ExternalIdentifier : "has identifiers"
    Device ||--o{ ConfigComparison : "is compared"
    ConfigVersion ||--o{ ConfigComparison : "is source version"
    ConfigVersion ||--o{ ConfigComparison : "is target version"

    User {
        bigint id PK
    }
    BackupPolicy {
        bigint id PK
        string name UK
        bool is_active
        smallint default_retry_count
        int default_timeout_seconds
        bigint created_by FK
    }
    BackupPolicyDevice {
        bigint id PK
        bigint policy_id FK
        bigint device_id FK
        bool enabled
    }
    BackupSchedule {
        bigint id PK
        bigint policy_id FK
        string frequency
        string cron_expression
        string timezone
        datetime next_run_at
        bool is_active
    }
    BackupRun {
        bigint id PK
        bigint policy_id FK
        bigint triggered_by_id FK
        string trigger_type
        string status
        datetime started_at
        datetime finished_at
    }
    BackupAttempt {
        bigint id PK
        bigint run_id FK
        bigint device_id FK
        string status
        smallint attempt_number
        string oxidized_node_ref
        string oxidized_version_ref
    }
    Device {
        bigint id PK
        string name
        string hostname
        string management_ip
        bool is_demo
    }
    ConfigVersion {
        bigint id PK
        bigint device_id FK
        string source
        string external_ref
        datetime collected_at
        string checksum
        bigint created_by_id FK
    }
    ExternalIdentifier {
        bigint id PK
        bigint device_id FK
        string system
        string external_id
        bool is_active
    }
    ConfigComparison {
        bigint id PK
        bigint device_id FK
        bigint from_version_id FK
        bigint to_version_id FK
        bigint created_by_id FK
        string diff_external_ref
    }
```

### Restricciones representadas o relevantes

- `BackupPolicy.name` es único.
- `BackupPolicyDevice` tiene una restricción única por pareja `policy_id` y `device_id`.
- `BackupAttempt` tiene una restricción única por `run_id`, `device_id` y `attempt_number`.
- `ConfigVersion` tiene una restricción única por `device_id`, `source` y `external_ref`.
- `BackupRun.triggered_by` y `ConfigVersion.created_by` son relaciones opcionales; el creador de una política y de una comparación es obligatorio.
- `BackupPolicyDevice.policy` y `BackupSchedule.policy` se eliminan en cascada con la política. La ejecución protege la política contra eliminación; los dispositivos asociados a intentos, asignaciones y versiones también usan protección contra eliminación.
- Algunas reglas temporales y de consistencia se validan en `clean()` de los modelos Django. El diagrama no implica que todas estén implementadas como restricciones SQL.

## Diagrama de trazabilidad y límites de responsabilidad

Las flechas continuas describen relaciones o datos que SIGRED persiste. Las flechas discontinuas indican asociaciones conceptuales por referencia textual o un disparo que no se registra mediante una FK.

```mermaid
flowchart LR
    subgraph SIGRED["SIGRED"]
        P["BackupPolicy"]
        PD["BackupPolicyDevice"]
        S["BackupSchedule"]
        R["BackupRun"]
        A["BackupAttempt"]
        D["Device"]
        CV["ConfigVersion<br/>metadatos y referencia externa"]
        U["Usuario iniciador"]
        P -->|"incluye"| PD
        PD -->|"identifica"| D
        P -->|"origina"| R
        R -->|"contiene"| A
        A -->|"corresponde a"| D
        P -->|"define"| S
        U -->|"inicia, cuando aplica"| R
        D -->|"tiene metadatos de versión"| CV
        S -.->|"puede disparar; no se guarda FK"| R
        A -.->|"oxidized_version_ref: texto, sin FK"| CV
    end
    subgraph OXIDIZED["Oxidized"]
        OX["Nodo y configuración versionada"]
    end
    A -.->|"oxidized_node_ref y referencia de versión"| OX
    CV -.->|"external_ref identifica recurso externo"| OX
```

![Diagrama de trazabilidad entre SIGRED y Oxidized](./diagrama-trazabilidad-respaldos.svg)

La asociación entre `BackupAttempt.oxidized_version_ref` y `ConfigVersion.external_ref` debe entenderse como intención de vinculación mediante identificadores, no como integridad referencial garantizada por la base de datos. El contenido completo de configuración no aparece como campo de `ConfigVersion`; SIGRED conserva metadatos como origen, referencia externa, fecha de recolección y, opcionalmente, checksum y tamaño.

## Fuentes del modelo

- `backend/backups/models.py`: políticas, asignaciones, programaciones, ejecuciones, intentos, versiones y comparaciones.
- `backend/inventory/models.py`: dispositivos e identificadores externos.
- `backend/backups/migrations/0001_initial.py`: esquema inicial de respaldos y sus restricciones.
- `backend/inventory/migrations/0001_initial.py`: esquema inicial del inventario.
