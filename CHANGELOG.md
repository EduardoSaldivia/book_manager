# Registro de cambios

## Sprint 3

### [Ejercicio 7]

- Integración de `ServicioScraping` y `ServicioAuditoria` en `crear_aplicacion()` dentro de `main.py` y pasaje de instancias a la consola interactiva.
- Soporte para parámetros opcionales `scraping` y `auditoria` en el constructor de la clase `Consola` en `console.py`.
- Métodos auxiliares `_ejecutar_scraping()`, `_generar_reporte_excel()` y `_mostrar_historial_auditoria()` en la consola para interactuar con los nuevos servicios.
- Incorporación de las opciones 18, 19 y 20 al menú principal y al despachador de selección para la ejecución de scraping con umbral en ARS, generación de reportes Excel y consulta del historial de auditoría.

### [Ejercicio 6]

- Modelo `AuditoriaModelo` en `models.py` para persistir registros de auditoría (`accion`, `fecha`, `detalles`).
- Decorador de clase `@auditar_operaciones` en `auditoria.py` que intercepta métodos públicos de los servicios y registra ejecución, parámetros, estado (`correcto` o `error`) y excepciones en transacciones dedicadas.
- Clase `ServicioAuditoria` para consultar el historial cronológico de auditorías con límite parametrizable sin auto-auditarse.
- Decoración con `@auditar_operaciones` sobre `ServicioBase`, `ServicioPrecio`, `ServicioStock` y `ServicioCotizacionDolar` en `services.py`.

### [Ejercicio 5]

- Implementación de `generar_reporte_excel()` en `ServicioScraping` utilizando `openpyxl`.
- Carga y procesamiento del JSON de extracción más reciente.
- Estructuración de columnas requeridas: Libro, Precio interno, Precio web, Diferencia y Fecha de extracción.
- Exportación automática a `src/book_manager/reportes/reporte_cuspide_*.xlsx`.

### [Ejercicio 4]

- Comparación entre precio interno y precio web scraping.
- Umbral dinámico en ARS solicitado al usuario previo al escaneo.
- Exportación automática del reporte de discrepancias a formato CSV para su posterior descarga y análisis.


### [Ejercicio 3]

- Implementación de CuspideSpider, que busca los títulos del catálogo y limita cada búsqueda a los primeros diez resultados.
- Validación del ISBN para aceptar únicamente la misma edición del libro.
- Incorporación de Item Loader para limpiar los datos y convertir precios a decimales.
- Incorporación de Pipeline para validar los registros y quitar formas de pago duplicadas.
- Extracción de precio, imagen, medios de pago, descripción y fecha de extracción.

### [Ejercicio 2]
- Se agregó una función para ejecutar en orden los archivos SQL de migración.


### [Ejercicio 1]

- Se creó la rama Sprint_3 a partir de Sprint_2.
- Se agregaron las carpetas iniciales para el scraper y los reportes.

---

## Sprint 2

### [Ejercicio 8]

- Incorporación de opciones de menú para obtener cotizaciones por API, listar precios bimonetarios y exportar.
- Conversión con cotizaciones guardadas y tasas fijas de la base, sin consultas automáticas a internet.
- Exportación de un CSV con una columna por moneda, tipo y fecha de cotización.
- Conservación de importación JSON y comparación local con el catálogo de Cúspide.
- La consola permite consultar y administrar cotizaciones con sus campos de compra y venta.

### [Ejercicio 7]

- Implementación de obtener_cotizaciones en ServicioCotizacionDolar.
- Lectura de API_URL desde .env, descarga con tiempo límite y validación de la respuesta.
- Registro del valor de venta con fecha de actualización en Argentina.
- Inserción o actualización del lote completo dentro de una transacción.
- La importación conserva compra y venta; las casas sin mapeo se omiten y no cancelan el resto del lote.
- Se agregó una migración que traslada los valores anteriores a compra y venta, preservando los 17 registros.

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
- Se completaron las relaciones bidireccionales de SQLAlchemy usando back_populates.

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