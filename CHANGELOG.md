# Registro de cambios

## Sprint 2

### [Ejercicio 7]

- Implementación de obtener_cotizaciones en ServicioCotizacionDolar.
- Lectura de API_URL desde .env, descarga con tiempo límite y validación de la respuesta.
- Registro del valor de venta con fecha de actualización en Argentina.
- Inserción o actualización del lote completo dentro de una transacción.

### [Ejercicio 6]

- Sustitución de repositorios CSV por repositorios SQLAlchemy para las ocho entidades.
- Reconstrucción de entidades y relaciones antes de cerrar las sesiones.
- Integración de main y precarga con Supabase, sin carga ni sincronización automática al iniciar.
- Actualización del título de consola a Sprint 2 y de los mensajes de persistencia.

### [Ejercicio 5]

- Incorporación de una copia de los ocho CSV de funcionamiento del Sprint 1.
- Validación de encabezados, tipos, claves y referencias antes de importar.
- Generación de ocho archivos SQL ordenados por dependencias.
- Migración en una transacción, conservando las claves existentes sin duplicarlas.

### [Ejercicio 4]

- Definición de las ocho tablas con claves primarias, relaciones y restricciones.
- Incorporación del método crear_tablas para crear las tablas en Supabase.
- Incorporación de verificar_transaccion.py para comprobar el rollback con los modelos.
- Verificación previa en Supabase: la inserción de prueba fue revertida.

### [Ejercicio 3]

- Implementación del administrador de contexto transaccion.
- Confirmación automática al finalizar y rollback ante errores.
- Cierre de la sesión al salir del bloque de trabajo.

### [Ejercicio 2]

- Implementación de ConexionDB con SQLAlchemy y psycopg.
- Lectura de configuración desde .env y conexión cifrada a PostgreSQL.
- Incorporación de métodos para comprobar y cerrar la conexión.

### [Ejercicio 1]

- Preparación de la rama Sprint_2 a partir del último estado de Sprint_1.
- Preparación de las carpetas database, models y migrations/sql.
- Incorporación de dependencias, plantilla .env.example y exclusión de credenciales.
- Actualización del README con el objetivo, la introducción y el contexto del Sprint 2.

---

## Sprint 1



## [DEjercicio 7] Integración y ejecución

- Conexión de repositorios, servicios, precarga y consola en main.py.
- Opciones --precargar, --sin-menu y --datos; precarga en el primer inicio.
- README con instrucciones para ejecutar el proyecto y comportamiento de las cotizaciones.

## [Ejercicio 6] Interfaz de consola

- Menús para los ocho CRUD, conversiones, histórico e inventario.
- Consultas externas a pedido; confirmación antes de guardar una cotización.
- Presentación del Grupo 44, tablas y valores monetarios con dos decimales.
- Inventario con una lectura del stock y resumen disponible en la opción 12.

## [Ejercicio 5] Datos iniciales y precarga

- Ocho CSV con al menos diez registros por entidad y un catálogo de cien libros.
- Precarga de registros ausentes sin reemplazar los existentes.
- Sincronización de tasas fijas desde monedas.csv.

## [Ejercicio 4] Servicios y consultas externas

- Reglas de negocio, validación de relaciones y protección de borrados.
- Conversiones con cotizaciones guardadas para USD y tasas fijas para otras monedas.
- Clientes de DolarAPI y del catálogo público de Cúspide.

## [DEjercicio 3] Repositorios y persistencia CSV

- Interfaces y operaciones CRUD para las ocho entidades.
- Reconstrucción de relaciones y consulta del histórico por tipo.
- Búsquedas por identificador que construyen solo el registro solicitado.

## [Ejercicio 2] Entidades del sistema

- Ocho entidades con encapsulación, relaciones y validaciones.
- Decimal para importes y date para fechas; tasas fijas opcionales en Moneda.

## [Ejercicio 1] Estructura del proyecto

- Estructura de carpetas y archivos del Sprint 1.
- README, dependencias y exclusiones de archivos locales.