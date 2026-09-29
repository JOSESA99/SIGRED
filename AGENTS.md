# Instrucciones para trabajar en SIGRED

SIGRED es el Sistema de Gestión de Red para la OTI de la Universidad Nacional de San Martín. Antes de implementar cambios, leer:

- `docs/CONTEXTO_PROYECTO.md`: contexto funcional, alcance y distribución del trabajo.
- `docs/ESTADO_ACTUAL.md`: estado técnico comprobado en el repositorio.
- `docs/MODELO_DATOS.md`: propuesta inicial del modelo de datos y orden de implementación.

Reglas de trabajo:

- Inspeccionar los archivos existentes antes de modificarlos.
- Conservar el trabajo existente y las migraciones aplicadas.
- No reiniciar la base de datos ni eliminar datos para simplificar el desarrollo.
- Gestionar cambios de esquema con modelos y migraciones de Django.
- Verificar compatibilidad con SQL Server antes de usar campos o restricciones poco comunes.
- No imprimir, copiar a documentación ni versionar secretos de `backend/.env`.
- Crear datos de demostración claramente marcados como tales cuando no haya acceso a equipos reales.
- No asumir que todos los dispositivos admiten los mismos protocolos, comandos o métricas.
- Mantener separadas las responsabilidades: Santiago en respaldos/configuraciones, Kevin en monitoreo/incidentes, ambos en inventario común, usuarios, permisos e integración.
- Documentar qué pertenece a SIGRED y qué queda gestionado por Oxidized o Zabbix.
- No crear tablas de dominio ni ejecutar nuevas migraciones sin revisar antes el diseño propuesto.
