#  Book Manager — Grupo 44

## Sprint 2

Aplicación de consola en Python para gestionar una librería. Esta entrega amplía
el Sprint 1 con PostgreSQL alojado en Supabase y SQLAlchemy.

## Objetivo

Migrar los datos de archivos CSV a tablas relacionales, aplicar transacciones y
mantener la integridad de los datos. Generar archivos SQL de inserción y adaptar
las operaciones del sistema a la base de datos. Incorporar cotizaciones por API,
precios en pesos y otra moneda, y exportación de precios para todas las monedas.

## Introducción y contexto

Una librería necesita centralizar libros, géneros, editoriales, monedas, precios,
existencias y cotizaciones. El Sprint 1 conserva esa información en CSV y utiliza
referencias JSON locales. En el Sprint 2 la base relacional permite mantener
las relaciones entre registros y confirmar o revertir operaciones completas.

## Estado de la entrega

Ejercicios 1 a 7 incorporados: el servicio ya permite descargar y registrar cotizaciones por API. Las nuevas opciones de menú y exportación se incorporan en el ejercicio 8.

## Datos y cotizaciones

Los CSV del Sprint 1 se conservan como origen de la migración. Los archivos SQL
describen ese origen y se generan en orden de dependencias. Repetir la migración
conserva los registros con claves existentes; no los reemplaza ni los duplica.

Para el dólar se utiliza el valor de venta y la fecha informada por la fuente,
convertida al horario de Argentina. Una importación por API puede actualizar
el mismo tipo y fecha. Las conversiones utilizan cotizaciones ya guardadas;
las otras monedas conservan sus tasas fijas en la base.

El catálogo de referencia de Cúspide sigue siendo un JSON local. Su lectura no
consulta la web de Cúspide. Las credenciales se guardan en .env, excluido de Git;
.env.example contiene solamente una plantilla.

## Tecnologías

- Python y programación orientada a objetos.
- SQLAlchemy, psycopg y PostgreSQL en Supabase.
- python-dotenv y requests.
- CSV y SQL para migración; JSON para referencias locales.

---

Sistema de gestión de inventario para una librería, desarrollado en **Python** como parte del **Sprint 1**.

El proyecto permite administrar libros, precios, stock y diferentes datos asociados al catálogo, aplicando conceptos de **Programación Orientada a Objetos** y **persistencia de datos mediante archivos CSV**.

---

##  Sprint 1

En esta primera etapa se desarrolla una aplicación de consola orientada a la gestión integral del inventario de una librería.

El sistema busca centralizar la información de los libros y facilitar operaciones relacionadas con precios, monedas, cotizaciones y stock.

---

##  Objetivo

El objetivo principal del proyecto es aplicar los conceptos vistos durante la cursada mediante el desarrollo de una solución que permita gestionar:

-  Libros
-  Géneros
-  Editoriales
-  Monedas
-  Precios
-  Stock
-  Cotizaciones

La información se almacena utilizando archivos **CSV**, permitiendo conservar los datos entre ejecuciones del programa.

---

##  Contexto

Una librería necesita modernizar la forma en la que administra su inventario.

Además de gestionar libros y disponibilidad de stock, el sistema debe contemplar productos cuyos precios pueden estar expresados en distintas monedas.

Para resolver esta necesidad, **Book Manager** incorpora diferentes fuentes de información para trabajar con precios y cotizaciones.

---

##  Cotizaciones y comparación de precios

El proyecto contempla:

- Cotizaciones del dólar almacenadas localmente.
- Consulta de cotizaciones actualizadas mediante **DolarAPI**.
- Conversión y manejo de precios en diferentes monedas.
- Comparación de precios con el catálogo online de **Cúspide**.

Esto permite contar con información de referencia para analizar y actualizar los precios de los libros.

---

##  Tecnologías utilizadas

- **Python**
- **Programación Orientada a Objetos**
- **CSV**
- **DolarAPI**
- Consultas a información externa
- Aplicación ejecutada desde consola

---

##  Funcionalidades principales

El sistema permite gestionar la información necesaria para mantener actualizado el catálogo de una librería, incluyendo:

- Alta y consulta de libros.
- Administración de géneros y editoriales.
- Gestión de monedas.
- Manejo de precios.
- Control de stock.
- Registro de cotizaciones.
- Consulta de cotización del dólar.
- Comparación de precios con fuentes externas.

---

##  Grupo 44

- Cristian Vera
- Dario Verdún
- Sergio Sanchez
- Eduardo Saldivia

---

>  **Book Manager** busca integrar los conceptos de programación, persistencia de datos y consumo de información externa en una solución práctica para la gestión de una librería.