# Requisitos funcionales, de seguridad y operación del módulo de respaldos

## 1. Propósito y alcance

Este documento especifica los requisitos del módulo de respaldos y gestión de configuraciones de SIGRED para la OTI de la Universidad Nacional de San Martín. Incluye la frecuencia de recolección, conservación de versiones y copias, y controles de acceso.

SIGRED administra políticas, ejecuciones, resultados, permisos, referencias a versiones y planes de recuperación. Oxidized realiza la conexión técnica a los dispositivos y conserva el historial de configuraciones. SIGRED no debe duplicar ese historial en SQL Server sin una decisión de arquitectura aprobada.

La integración real con Oxidized, la programación periódica y el seguimiento de resultados todavía están pendientes. Los parámetros de frecuencia y conservación de este documento son una propuesta operativa inicial para aprobación de la OTI; no representan una política institucional ya aprobada. Los dispositivos de demostración no constituyen evidencia de respaldo de equipos reales.

## 2. Actores y responsabilidades

- **Administrador SIGRED:** administra usuarios, permisos, políticas e integración.
- **Operador de respaldos:** consulta cobertura e historial y puede iniciar ejecuciones autorizadas.
- **Aprobador de recuperaciones:** revisa y aprueba o rechaza planes de recuperación. Debe ser distinto del solicitante cuando sea operativamente posible.
- **Auditor o consultor:** consulta el historial y los registros que le permita su rol, sin ejecutar ni modificar respaldos.
- **SIGRED:** coordina el flujo, aplica permisos y registra resultados y referencias.
- **Oxidized:** obtiene y conserva las configuraciones y sus versiones.
- **OTI:** autoriza el acceso a equipos reales, aprueba la política de conservación y coordina las recuperaciones.

## 3. Requisitos funcionales

| ID | Requisito |
|---|---|
| RF-01 | El módulo permitirá crear, activar, desactivar y consultar políticas de respaldo con descripción, dispositivos asignados, tiempo máximo y cantidad de reintentos. |
| RF-02 | Cada dispositivo incluido deberá existir en el inventario, tener capacidad de respaldo confirmada y contar con un identificador Oxidized activo antes de permitir una ejecución real. La falta de validación impedirá marcarlo como protegido. |
| RF-03 | El módulo permitirá ejecuciones manuales y programadas. Cada ejecución registrará política, tipo de disparador, usuario iniciador cuando corresponda, fechas, estado y resumen. |
| RF-04 | Cada ejecución tendrá un resultado individual por dispositivo. Se registrarán estado, número de intento, marcas de tiempo, referencia externa de nodo/versión y motivo del error cuando falle. Un error en un equipo no ocultará los resultados de los demás. |
| RF-05 | Los estados de ejecución distinguirán, como mínimo, pendiente, en curso, exitosa, parcial, fallida y cancelada. El estado global reflejará los resultados de los intentos individuales. |
| RF-06 | El módulo permitirá consultar cobertura por dispositivo y política, última ejecución, último resultado, historial de versiones y errores, con filtros por unidad, ubicación, dispositivo, período y estado. |
| RF-07 | Se podrán registrar metadatos de cada versión, incluyendo dispositivo, origen, fecha de recolección, referencia externa y, cuando Oxidized lo proporcione, checksum y tamaño. El contenido completo permanecerá en Oxidized salvo aprobación de una arquitectura distinta. |
| RF-08 | Se podrán registrar comparaciones entre dos versiones del mismo dispositivo y referenciar el diferencial conservado por el sistema externo. |
| RF-09 | Un usuario autorizado podrá preparar un plan de recuperación indicando dispositivo, versión seleccionada y motivo. La recuperación requerirá aprobación y coordinación de la OTI; SIGRED no la ejecutará automáticamente como comportamiento inicial. |
| RF-10 | El módulo distinguirá datos reales de datos de demostración. Las simulaciones solo podrán usar dispositivos marcados como demo y deberán identificarse como ficticias en los resultados. |
| RF-11 | Una ejecución fallida deberá conservar su código y mensaje de error y permitir reintentos según la política, sin borrar ni sobrescribir el historial previo. |
| RF-12 | Los eventos de administración de políticas, ejecuciones, aprobaciones, consultas o exportaciones sensibles y recuperaciones deberán quedar trazables con actor, fecha, objeto y resultado cuando la función de auditoría esté disponible. |

## 4. Requisitos de frecuencia y programación

La siguiente tabla propone la frecuencia inicial. La programación debe configurarse en hora local `America/Lima` y evitar ventanas de mantenimiento de la OTI.

| Tipo de respaldo | Frecuencia propuesta | Condición |
|---|---|---|
| Recolección periódica de configuraciones | Una vez al día, a las 02:00 | Aplicable solo a dispositivos con compatibilidad, conectividad y autorización confirmadas. |
| Recolección por cambio planificado | Bajo demanda, antes y después del cambio | La solicita un operador autorizado y se vincula al cambio o motivo operativo. |
| Dispositivos críticos | Diaria; bajo demanda ante cambios autorizados | La OTI puede establecer una frecuencia mayor si valida capacidad, impacto y necesidades de recuperación. |
| Reintento por fallo transitorio | Hasta 2 reintentos adicionales por ejecución | Con espera configurable; la integración deberá evitar una tormenta de solicitudes y exponer fallos persistentes. |
| Copia secundaria del repositorio de configuraciones | Diaria, después de la ventana de recolección | Debe verificarse el resultado de la copia sin interrumpir las operaciones de Oxidized. |

Una programación no se considerará operativa hasta que el programador periódico y el seguimiento del resultado real de Oxidized estén implementados y probados. Si no se puede determinar que la configuración fue recolectada, el resultado no se reportará como exitoso.

## 5. Requisitos de conservación y copias

Los siguientes períodos son valores iniciales propuestos para que la OTI los confirme según sus obligaciones y capacidad de almacenamiento:

| Información o copia | Conservación propuesta | Ubicación y propósito |
|---|---|---|
| Versiones de configuraciones accesibles para recuperación | Mínimo 12 meses | Repositorio Git de Oxidized en almacenamiento primario. Debe conservar versiones suficientes para comparar y recuperar configuraciones dentro del período. |
| Copia secundaria del repositorio de Oxidized | Copia diaria; conservar puntos diarios de 30 días y un punto mensual de 12 meses | Almacenamiento separado del servidor primario, protegido contra eliminación o alteración accidental desde la cuenta de servicio de Oxidized. |
| Metadatos de ejecuciones, intentos, resultados y planes de recuperación | Mínimo 5 años | Base de datos SIGRED, sujeto a las reglas de retención documental de la UNSM y a la capacidad de SQL Server. |
| Datos ficticios de demostración | Mientras sean necesarios para desarrollo/pruebas | Deben estar claramente marcados y no mezclarse con reportes de cobertura real. |

La OTI deberá aprobar los plazos definitivos antes de habilitar respaldos de producción. La eliminación por vencimiento será controlada, trazable y nunca deberá eliminar la única copia recuperable dentro del período aprobado. Una retención legal o investigación operativa suspenderá la eliminación de los elementos afectados.

La copia secundaria no sustituye al repositorio primario: deberá almacenarse en un sistema o ubicación independiente, utilizar cifrado en tránsito y en reposo, limitar quién puede borrar o restaurar copias y mantener un registro del último resultado verificado. La tecnología de réplica, almacenamiento externo y protección inmutable queda pendiente de selección por la OTI.

## 6. Requisitos de seguridad y acceso a las copias

### 6.1 Control de acceso

Los permisos se asignarán por rol y mínimo privilegio. La siguiente matriz define el acceso requerido:

| Acción | Administrador SIGRED | Operador de respaldos | Aprobador de recuperaciones | Auditor/consulta |
|---|---:|---:|---:|---:|
| Consultar estado, cobertura e historial | Sí | Sí | Sí | Sí, solo lectura |
| Crear o modificar políticas y programación | Sí | No | No | No |
| Ejecutar respaldo manual o solicitar reintento | Sí | Sí | Según permiso asignado | No |
| Consultar configuración completa o diferencial | Solo si está autorizado | Solo si está autorizado | Solo si está autorizado | Solo si está autorizado |
| Crear plan de recuperación | Sí | Sí | Sí | No |
| Aprobar o rechazar recuperación | No por defecto | No | Sí | No |
| Ejecutar recuperación en un equipo | No automáticamente | No automáticamente | Solo con autorización específica de la OTI | No |
| Administrar acceso al repositorio o a copias secundarias | Personal designado por la OTI | No | No | No |

El acceso a metadatos de ejecución no implica acceso al contenido de configuraciones. Las configuraciones pueden contener datos sensibles; su lectura, descarga o exportación debe restringirse a personal autorizado y dejar evidencia de auditoría. El acceso directo al repositorio y a la copia secundaria se limitará a las cuentas de servicio y administradores designados, no a todos los usuarios de SIGRED.

### 6.2 Protección de credenciales y contenido

- Las contraseñas, claves privadas, tokens y secretos de dispositivos no se almacenarán en texto plano en SIGRED, SQL Server, registros de aplicación ni documentación.
- Oxidized recibirá las credenciales mediante un mecanismo seguro gestionado por la OTI. SIGRED almacenará únicamente referencias cuando corresponda.
- La comunicación SIGRED–Oxidized y las transferencias de copias se limitarán a redes autorizadas y usarán TLS cuando atraviesen una red compartida o no confiable.
- El repositorio primario y las copias secundarias tendrán cifrado en reposo, con claves bajo control administrativo de la OTI.
- La API de Oxidized no se expondrá públicamente; se restringirá por red y autenticación/proxy seguro según el entorno.
- No se mostrarán secretos ni configuraciones completas en mensajes de error, logs generales o notificaciones.
- Los permisos de cuentas de servicio en dispositivos serán los mínimos necesarios para recolectar configuraciones; no se habilitarán comandos o protocolos sin validar cada modelo.

### 6.3 Integridad y auditoría

- Se verificará la integridad de las copias mediante checksums o el mecanismo equivalente del sistema de almacenamiento.
- Las operaciones de acceso, exportación, aprobación y recuperación deberán asociarse a una identidad individual; se evitarán cuentas compartidas para usuarios humanos.
- Los registros de auditoría serán de solo adición para los roles operativos y tendrán controles contra modificación no autorizada.
- Una restauración requerirá identificar la versión exacta, el dispositivo destino, el solicitante, el aprobador, la fecha y el resultado.

## 7. Requisitos de operación y recuperación

1. **Alta de dispositivo:** validar inventario, capacidades, identificador Oxidized, autorización y conectividad antes de incluirlo en una política real.
2. **Supervisión diaria:** revisar ejecuciones incompletas y fallidas; notificar o generar una tarea operativa cuando un dispositivo no tenga una versión exitosa en las últimas 24 horas.
3. **Atención de fallos:** registrar causa conocida, intentos efectuados y acción pendiente. No indicar cobertura vigente cuando la última recolección exceda el intervalo aprobado.
4. **Verificación de copias:** comprobar diariamente que la copia secundaria finalizó y que los datos son legibles/integrables; alertar a la OTI ante fallo o retraso.
5. **Prueba de recuperación:** realizar una prueba controlada al menos trimestralmente en un equipo de laboratorio o entorno autorizado, documentando versión usada, resultado y duración. No modificar equipos de producción como prueba sin aprobación expresa.
6. **Recuperación real:** seguir el plan aprobado por la OTI, confirmar compatibilidad y versión, registrar aprobación/ejecutor/resultado y verificar el servicio después del cambio.
7. **Revisión de acceso:** revisar trimestralmente los usuarios, grupos y cuentas de servicio con acceso al contenido o copias; revocar accesos que ya no sean necesarios.
8. **Continuidad:** mantener documentado cómo recuperar el repositorio de Oxidized y su configuración desde la copia secundaria, incluyendo responsables y ubicación de las claves necesarias. Las claves no se incluirán en este documento.
9. **Zona horaria:** registrar y presentar fechas de operación en `America/Lima`, conservando marcas de tiempo consistentes entre SIGRED y Oxidized.

## 8. Criterios de aceptación

- Una política no puede incluir para respaldos reales dispositivos cuya capacidad o identificador Oxidized no estén validados.
- Una ejecución registra estados y resultados por dispositivo, incluyendo fallos parciales y errores explicables.
- Una simulación no contacta Oxidized ni equipos reales y es identificable como demostración.
- Los usuarios sin permiso no pueden ejecutar respaldos, cambiar políticas, consultar contenido restringido ni aprobar recuperaciones.
- Las recuperaciones quedan sujetas a aprobación y no se ejecutan automáticamente.
- La frecuencia, período de conservación y roles aprobados por la OTI se reflejan en la configuración operativa y se pueden auditar.
- Existe una copia secundaria verificada y una prueba documentada de recuperación antes de declarar el servicio listo para producción.

## 9. Decisiones pendientes para producción

- Aprobación de la frecuencia diaria propuesta y de ventanas de mantenimiento.
- Aprobación formal de los períodos de conservación y de las reglas institucionales aplicables.
- Selección de infraestructura para Oxidized, repositorio primario, copia secundaria y protección contra eliminación.
- Selección del mecanismo de gestión de secretos y de cifrado.
- Definición de usuarios/grupos autorizados a ver o exportar configuraciones.
- Implementación del programador, seguimiento de resultados reales, alertas y limpieza controlada por retención.
- Definición de objetivos institucionales de tiempo de recuperación (RTO) y punto de recuperación (RPO), que no se presuponen en este documento.
