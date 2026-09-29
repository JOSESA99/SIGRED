# Contexto del proyecto SIGRED

SIGRED significa Sistema de Gestión de Red. Es un proyecto de prácticas preprofesionales desarrollado por Santiago y Kevin para la Oficina de Tecnología e Información (OTI) de la Universidad Nacional de San Martín, Perú.

## Problema

La universidad necesita respaldos centralizados de las configuraciones de sus dispositivos de red y un monitoreo que permita detectar fallas, gestionar incidentes y disponer de configuraciones recuperables ante cortes de energía, averías u otros problemas operativos.

El alcance previsto incluye la OTI y aproximadamente ocho facultades. Todavía no existe un inventario completo confirmado ni una lista definitiva de modelos y capacidades. Hay principalmente switches Cisco y también equipos Check Point. No se debe asumir que todos admiten los mismos protocolos, comandos, métricas o formas de recuperación.

SIGRED debe ser un sistema completo y mantenible, con funciones justificadas por estas necesidades. No debe reducirse a un dashboard ni agregar complejidad sin propósito operativo.

## Distribución del trabajo

- Santiago: módulo de respaldos y gestión de configuraciones.
- Kevin: módulo de monitoreo e incidentes.
- Ambos: inventario común, usuarios, permisos e integración general.

El trabajo abarca este ciclo hasta el 4 de diciembre de 2026 y continuará aproximadamente de marzo a julio de 2027. Se desarrollará progresivamente el mismo sistema.

## Alcance funcional propuesto

### Inventario y estructura institucional

- Facultades o unidades, ubicaciones y dispositivos.
- Fabricante, modelo, dirección de administración y estado.
- Relación entre cada equipo, su ubicación y su unidad.
- Identificadores para vincular equipos con servicios externos.
- Evaluación de integración con el inventario institucional existente, confirmando tecnología y acceso antes de implementarla.

### Respaldos y configuraciones

Responsable principal: Santiago.

- Políticas y programación de respaldos.
- Ejecuciones manuales y programadas.
- Estados, errores y reintentos.
- Historial de versiones de configuraciones.
- Comparación de cambios entre versiones.
- Validación y cobertura de respaldos.
- Preparación de recuperaciones supervisadas.
- Auditoría de acciones.

### Monitoreo e incidentes

Responsable principal: Kevin.

- Disponibilidad de dispositivos.
- Interfaces y métricas compatibles con cada equipo.
- Reglas y umbrales de alertas.
- Eventos e incidentes.
- Reconocimiento, asignación, seguimiento y cierre de incidentes.
- Ventanas de mantenimiento.
- Dependencias y topología cuando existan datos suficientes.
- Historial e indicadores.

### Funciones compartidas

- Autenticación y permisos por función.
- Panel general y vistas detalladas por dispositivo.
- Informes y auditoría.
- Configuración de integraciones.

## Integraciones previstas

Se contempla utilizar Oxidized como motor de recolección de configuraciones y Zabbix como motor de monitoreo.

SIGRED aportará la aplicación propia, los flujos de trabajo, la integración, los permisos, la trazabilidad y las vistas unificadas. Debe documentarse claramente qué desarrolla el equipo y qué proporcionan las herramientas externas.

Las integraciones con Oxidized y Zabbix todavía no están instaladas ni verificadas.

No se debe duplicar automáticamente en SQL Server todo el historial de métricas de Zabbix ni almacenar sin evaluación todas las configuraciones como campos de texto. Debe definirse qué información pertenece a SIGRED y qué conserva cada motor.

Los accesos a dispositivos reales, las pruebas de restauración y las modificaciones de configuraciones requieren coordinación y autorización de la OTI. Para el desarrollo inicial se pueden usar datos de demostración identificados como tales.
