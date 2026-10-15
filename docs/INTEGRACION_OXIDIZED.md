# Integración de SIGRED con Oxidized

## Estado actual

El cliente de SIGRED para la API de Oxidized está implementado y probado con respuestas simuladas. La integración permanece desactivada porque Oxidized no está instalado en el equipo de desarrollo y todavía no se han autorizado pruebas con dispositivos reales.

Variables de entorno previstas, sin secretos:

```text
OXIDIZED_ENABLED=false
OXIDIZED_BASE_URL=http://127.0.0.1:8888
OXIDIZED_TIMEOUT_SECONDS=10
```

No se debe cambiar `OXIDIZED_ENABLED` a `true` hasta que el servicio responda y su acceso esté restringido adecuadamente.

## Operaciones soportadas por el cliente

- listar nodos conocidos por Oxidized;
- solicitar que Oxidized recargue su origen de nodos;
- mover un nodo al inicio de la cola de recolección;
- obtener la configuración conservada para un nodo.

El cliente no guarda credenciales de dispositivos ni modifica configuraciones.

## Instalación pendiente

En el equipo revisado no están instalados Oxidized, Docker ni una distribución de WSL. Para un entorno local se recomienda instalar Oxidized dentro de Linux o utilizar un contenedor. Esa instalación es una tarea de infraestructura separada del backend Django.

Antes de realizarla se debe decidir:

1. si el entorno autorizado será una máquina Linux, WSL o un servidor de la OTI;
2. dónde se almacenará el repositorio Git de configuraciones;
3. cómo recibirá Oxidized la lista de nodos;
4. cómo se suministrarán credenciales sin guardarlas en SIGRED;
5. qué dispositivo de laboratorio está autorizado para la primera prueba.

## Seguridad

- Mantener la API escuchando solo en una interfaz privada o local.
- Si SIGRED y Oxidized están en equipos diferentes, proteger el acceso mediante red restringida y un proxy con autenticación y TLS.
- Usar cuentas de dispositivos con los privilegios mínimos necesarios para consultar configuraciones.
- No usar inicialmente dispositivos de producción ni automatizar restauraciones.

Referencias oficiales:

- https://github.com/ytti/oxidized
- https://github.com/ytti/oxidized-web
- https://github.com/ytti/oxidized/blob/master/docs/Configuration.md
