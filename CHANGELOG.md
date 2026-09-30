# Registro de cambios

## [Día 8] Sustitución de APIs por JSONs

- Lectura de cotizaciones y del catálogo de Cúspide desde archivos JSON locales en lugar de DolarAPI y la web de Cúspide.
- Módulo común para leer y validar los JSON; se quitó la dependencia de requests.

## [Día 7] Integración y ejecución

- Conexión de repositorios, servicios, precarga y consola en main.py.
- Opciones --precargar, --sin-menu y --datos; precarga en el primer inicio.
- README con instrucciones para ejecutar el proyecto y comportamiento de las cotizaciones.

## [Día 6] Interfaz de consola

- Menús para los ocho CRUD, conversiones, histórico e inventario.
- Consultas externas a pedido; confirmación antes de guardar una cotización.
- Presentación del Grupo 44, tablas y valores monetarios con dos decimales.
- Inventario con una lectura del stock y resumen disponible en la opción 12.

## [Día 5] Datos iniciales y precarga

- Ocho CSV con al menos diez registros por entidad y un catálogo de cien libros.
- Precarga de registros ausentes sin reemplazar los existentes.
- Sincronización de tasas fijas desde monedas.csv.

## [Día 4] Servicios y consultas externas

- Reglas de negocio, validación de relaciones y protección de borrados.
- Conversiones con cotizaciones guardadas para USD y tasas fijas para otras monedas.
- Clientes de DolarAPI y del catálogo público de Cúspide.

## [Día 3] Repositorios y persistencia CSV

- Interfaces y operaciones CRUD para las ocho entidades.
- Reconstrucción de relaciones y consulta del histórico por tipo.
- Búsquedas por identificador que construyen solo el registro solicitado.

## [Día 2] Entidades del sistema

- Ocho entidades con encapsulación, relaciones y validaciones.
- Decimal para importes y date para fechas; tasas fijas opcionales en Moneda.

## [Día 1] Estructura del proyecto

- Estructura de carpetas y archivos del Sprint 1.
- README, dependencias y exclusiones de archivos locales.
