# 📚 Book Manager — Grupo 44

Sistema de gestión de inventario para una librería, desarrollado en **Python** como parte del **Sprint 2**.

El proyecto permite administrar libros, precios, stock y diferentes datos asociados al catálogo, aplicando conceptos de **Programación Orientada a Objetos** y ampliando la persistencia de archivos CSV a una base de datos relacional.

---

## 🚀 Sprint 2

Esta entrega parte del último estado del Sprint 1 y amplía Book Manager para
persistir sus datos en PostgreSQL, alojado en Supabase, mediante SQLAlchemy.

## 🎯 Objetivo

Migrar los datos de los archivos CSV a tablas relacionadas, aplicando normalización,
conexión segura y transacciones. Generar archivos SQL de inserción y adaptar los
repositorios para realizar las operaciones del sistema sobre la base de datos.

El alcance también incluye obtener y registrar cotizaciones desde la API del dólar,
mostrar precios en pesos y otra moneda seleccionada, y exportar precios a CSV
para todas las monedas.

## 💡 Introducción y contexto

Una librería necesita centralizar su catálogo, precios y existencias, manteniendo
la relación entre libros, géneros, editoriales, monedas y cotizaciones.
La base relacional permitirá conservar la integridad de esas relaciones y
confirmar o revertir operaciones completas mediante transacciones.

El Sprint 1 aporta las entidades, las reglas de negocio, la consola y los datos
de origen. La incorporación de la base de datos se realiza por ejercicios:
la migración, los repositorios y las nuevas opciones de menú se integrarán
en las siguientes etapas. La consola existente todavía utiliza los CSV hasta
completar esa integración.

---

## 💵 Cotizaciones y comparación de precios

Funcionalidades heredadas del Sprint 1:

- Cotizaciones del dólar almacenadas localmente.
- Lectura de cotizaciones desde un archivo **JSON local**, con confirmación antes de guardarlas.
- Conversión y manejo de precios en diferentes monedas.
- Comparación de precios por ISBN con el archivo local **precios_cuspide.json**.

El JSON de cotizaciones contiene referencias de Dolarito y tres escenarios sintéticos identificados como Simulación A, B y C. El catálogo JSON contiene la tabla de precios de Cúspide aportada por el grupo. Los archivos indican su fuente y fecha; son copias locales que no se actualizan automáticamente. Estos lectores locales se conservan del Sprint 1. La consulta a la API del dólar
se incorporará en el ejercicio 7 del Sprint 2.

---

## 🛠️ Tecnologías utilizadas

- **Python**
- **Programación Orientada a Objetos**
- **PostgreSQL en Supabase**
- **SQLAlchemy y psycopg**
- **python-dotenv y requests**
- **CSV**
- **JSON**
- Lectura de archivos JSON locales
- Aplicación ejecutada desde consola

---

## 📂 Funcionalidades principales

El sistema permite gestionar la información necesaria para mantener actualizado el catálogo de una librería, incluyendo:

- Alta y consulta de libros.
- Administración de géneros y editoriales.
- Gestión de monedas.
- Manejo de precios.
- Control de stock.
- Registro de cotizaciones.
- Consulta de cotizaciones del dólar desde JSON.
- Comparación de precios con un catálogo JSON local.

---

## 👥 Grupo 44

- Cristian Vera
- Dario Verdún
- Sergio Sanchez
- Eduardo Saldivia

---

> 📌 **Book Manager** busca integrar los conceptos de programación, persistencia de datos y lectura de datos JSON locales en una solución práctica para la gestión de una librería.
