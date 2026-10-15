# Flujo funcional de inventario y respaldos

Este documento define cómo el inventario compartido alimentará el módulo de respaldos de SIGRED. Su objetivo es acordar el comportamiento antes de crear nuevas tablas o integrar equipos reales.

## 1. Inventario como fuente común

Todo respaldo debe corresponder a un `Device` existente. El inventario debe indicar, como mínimo:

- unidad institucional y ubicación;
- nombre, hostname o dirección de administración;
- fabricante, modelo y tipo de dispositivo cuando se conozcan;
- estado operativo y criticidad;
- capacidad de conexión confirmada o pendiente;
- capacidad `oxidized_backup` confirmada o pendiente;
- referencia a credenciales seguras, nunca una contraseña en texto plano;
- identificador externo de Oxidized cuando la integración esté habilitada.

No se habilitará un dispositivo para respaldos solo por pertenecer al inventario. Su compatibilidad y acceso deben validarse individualmente.

## 2. Responsabilidad de cada sistema

### SIGRED

- Decide qué dispositivos deben respaldarse y bajo qué política.
- Programa solicitudes manuales o periódicas.
- Registra cada ejecución y el resultado por dispositivo.
- Presenta cobertura, último resultado, errores y referencias a versiones.
- Mantiene permisos, trazabilidad y planes de recuperación.

### Oxidized

- Se conecta técnicamente al dispositivo.
- Ejecuta los comandos adecuados para cada sistema operativo compatible.
- Obtiene la configuración y conserva su historial técnico.
- Produce versiones y diferencias, normalmente mediante su repositorio Git.

SIGRED no duplicará inicialmente el texto completo de todas las configuraciones. Guardará metadatos y referencias a las versiones conservadas por Oxidized.

## 3. Flujo de incorporación de un dispositivo

1. Un gestor registra o importa el dispositivo en el inventario.
2. Se confirma fabricante, modelo, ubicación y dirección de administración.
3. Se registran sus capacidades: SSH, API, respaldo con Oxidized u otras.
4. Se vincula un perfil de credenciales mediante una referencia segura.
5. Se prueba conectividad en un entorno autorizado por la OTI.
6. Si Oxidized es compatible, se registra su identificador externo.
7. El dispositivo queda disponible para asociarlo a una política de respaldo.

Hasta completar la validación, la capacidad de respaldo permanece como `pending_test`; no debe mostrarse como equipo protegido.

## 4. Flujo de un respaldo

```text
Usuario o programador
        ↓
SIGRED crea una ejecución
        ↓
SIGRED crea un intento por dispositivo
        ↓
Oxidized obtiene la configuración
        ↓
SIGRED registra resultado y referencia
        ↓
El usuario consulta cobertura, historial o diferencias
```

Una ejecución global puede terminar como:

- `success`: todos los dispositivos finalizaron correctamente;
- `partial`: algunos dispositivos finalizaron y otros fallaron;
- `failed`: ningún dispositivo pudo respaldarse o falló el proceso general;
- `canceled`: la ejecución fue cancelada de forma controlada.

Cada dispositivo tendrá su propio intento y mensaje de error. Un fallo no debe ocultar los respaldos exitosos de los demás equipos.

## 5. Recuperación

La primera versión de SIGRED preparará una recuperación supervisada, pero no modificará automáticamente equipos reales.

1. El usuario elige un dispositivo y una versión conocida.
2. Registra el motivo de la recuperación.
3. Un usuario autorizado revisa y aprueba o rechaza el plan.
4. La ejecución real se coordina con la OTI.
5. SIGRED registra quién aprobó, qué versión se usó y el resultado.

## 6. Condiciones para comenzar las tablas de respaldos

Antes de generar la migración del módulo se debe confirmar:

- cómo se instalará o accederá a Oxidized;
- dónde conservará Oxidized su repositorio de configuraciones;
- cómo se mapeará cada dispositivo con un nodo de Oxidized;
- qué mecanismo seguro almacenará las credenciales;
- qué usuarios podrán ejecutar, aprobar o solo consultar respaldos;
- qué periodicidades necesita realmente la OTI.

Mientras esas decisiones estén pendientes se pueden implementar políticas, ejecuciones e intentos con datos demo, pero no se deben simular accesos a equipos reales como si fueran respaldos verificados.
