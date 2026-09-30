# 📚 Book Manager — Grupo 44

Sistema de gestión de inventario para una librería, desarrollado en **Python** como parte del **Sprint 1**.

El proyecto permite administrar libros, precios, stock y diferentes datos asociados al catálogo, aplicando conceptos de **Programación Orientada a Objetos** y **persistencia de datos mediante archivos CSV**.

---

## 🚀 Sprint 1

En esta primera etapa se desarrolla una aplicación de consola orientada a la gestión integral del inventario de una librería.

El sistema busca centralizar la información de los libros y facilitar operaciones relacionadas con precios, monedas, cotizaciones y stock.

---

## 🎯 Objetivo

El objetivo principal del proyecto es aplicar los conceptos vistos durante la cursada mediante el desarrollo de una solución que permita gestionar:

- 📖 Libros
- 🏷️ Géneros
- 🏢 Editoriales
- 💱 Monedas
- 💰 Precios
- 📦 Stock
- 📈 Cotizaciones

La información se almacena utilizando archivos **CSV**, permitiendo conservar los datos entre ejecuciones del programa.

---

## 💡 Contexto

Una librería necesita modernizar la forma en la que administra su inventario.

Además de gestionar libros y disponibilidad de stock, el sistema debe contemplar productos cuyos precios pueden estar expresados en distintas monedas.

Para resolver esta necesidad, **Book Manager** incorpora diferentes fuentes de información para trabajar con precios y cotizaciones.

---

## 💵 Cotizaciones y comparación de precios

El proyecto contempla:

- Cotizaciones del dólar almacenadas localmente.
- Lectura de cotizaciones desde un archivo **JSON local**, con confirmación antes de guardarlas.
- Conversión y manejo de precios en diferentes monedas.
- Comparación de precios por ISBN con el archivo local **precios_cuspide.json**.

El JSON de cotizaciones contiene referencias de Dolarito y tres escenarios sintéticos identificados como Simulación A, B y C. El catálogo JSON contiene la tabla de precios de Cúspide aportada por el grupo. Los archivos indican su fuente y fecha; son copias locales que no se actualizan automáticamente. El sistema los lee sin consultar API ni conectarse a internet.

---

## 🛠️ Tecnologías utilizadas

- **Python**
- **Programación Orientada a Objetos**
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
