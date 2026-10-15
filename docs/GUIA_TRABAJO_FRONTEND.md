# Guia compartida para el frontend de SIGRED

Esta guia evita que los modulos de Santiago y Kevin terminen con estructuras o estilos incompatibles. Todavia no selecciona una plantilla visual: primero establece las condiciones que esa plantilla debe cumplir.

## Regla principal

Habra un solo frontend de SIGRED. Respaldos, monitoreo, inventario, usuarios e incidentes seran modulos dentro de la misma aplicacion, no proyectos visuales separados.

## Orden de trabajo

1. Confirmar el modelo y los flujos del modulo en el backend.
2. Exponer esos flujos mediante una API comun.
3. Documentar estados, permisos, errores y datos esperados.
4. Evaluar plantillas con datos de demostracion.
5. Elegir una sola plantilla y definir sus componentes compartidos.
6. Construir cada modulo usando esos componentes.

## Estructura visual que debe compartir todo SIGRED

- Barra lateral unica para Inventario, Respaldos, Monitoreo, Incidentes y Administracion.
- Cabecera comun con usuario, notificaciones y entorno.
- Tablas con el mismo buscador, filtros, paginacion y estados vacios.
- Etiquetas de estado y severidad con colores consistentes.
- Formularios, confirmaciones y mensajes de error reutilizables.
- Pantalla de detalle de dispositivo como punto de union entre inventario, respaldos y monitoreo.
- Control de acceso por permisos recibidos desde el backend.

## Responsabilidades

- Santiago mantiene los flujos y pantallas de respaldos y configuraciones.
- Kevin mantiene los flujos y pantallas de monitoreo e incidentes.
- Ambos acuerdan y reutilizan navegacion, componentes, tipos, permisos y pantalla de dispositivo.
- Ningun modulo debe crear una segunda estructura de navegacion o un sistema visual independiente.

## Criterios para escoger la plantilla

- Compatible con React y TypeScript.
- Licencia clara para el uso del proyecto.
- Componentes accesibles y adaptables a pantallas pequenas.
- Buen soporte para tablas, formularios, filtros, graficos y estados de carga.
- Personalizacion de colores e identidad de la UNSM sin depender de cambios fragiles.
- Mantenimiento activo y documentacion suficiente.
- Sin obligar a usar un backend, autenticacion o base de datos diferente de Django y SQL Server.

## Decisiones pendientes antes de crear el frontend

- Definir el estilo visual institucional permitido por la UNSM.
- Comparar dos o tres alternativas de plantilla con la misma pantalla de inventario.
- Elegir biblioteca de componentes y de graficos.
- Definir el contrato inicial de la API.
- Definir autenticacion y manejo de permisos desde el navegador.

El panel administrativo de Django es una herramienta interna de desarrollo y administracion. No reemplaza el frontend final de SIGRED.
