# Book Manager — Grupo 44

## Sprint 1

Aplicación de consola en Python para gestionar el inventario de una librería.

## Objetivo

Aplicar programación orientada a objetos y persistencia en archivos CSV para
administrar libros, géneros, editoriales, monedas, precios, stock y cotizaciones.

## Introducción y contexto

Una librería necesita modernizar su inventario y gestionar precios expresados
en distintas monedas. El proyecto incorpora cotizaciones del dólar guardadas,
consultas a DolarAPI a pedido y comparación de precios con el catálogo de Cúspide.

## Organización

El código se incorpora por ejercicios sobre la rama Sprint_1. Cada ejercicio
registra sus cambios en CHANGELOG.md. La aplicación incluye las capas de entidades, repositorios, servicios, precarga y consola.

## Entorno

Python 3.11 y dependencias declaradas en requirements.txt.

## Instalación y ejecución en Windows / PowerShell

Desde la raíz del repositorio:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para iniciar:

```powershell
cd src
..\.venv\Scripts\python.exe -m book_manager.main
```

Al terminar, `cd ..` vuelve a la raíz para trabajar con Git. La primera ejecución
carga los datos iniciales en `data/`. Esta carpeta se genera localmente y no se
versiona. Los CSV iniciales se conservan en `src/book_manager/migrations/csv/`.

Opciones (desde `src`):

- `--sin-menu`: prepara el sistema y termina sin abrir la consola.
- `--precargar`: agrega los registros iniciales que falten; no reemplaza los existentes.
- `--datos ../work/prueba`: utiliza otra carpeta para los datos de funcionamiento.

El resumen se muestra únicamente al elegir la opción 12. Inventario: opción 11.
CRUD: opciones 1 a 8. Conversiones: opción 9. Histórico: opción 10.

## Cotizaciones y fuentes externas

`monedas.csv` tiene la columna `cotizacion_ars`: ARS por una unidad de moneda.
ARS vale 1; USD deja ese campo vacío porque utiliza el histórico de cotizaciones.
Las demás monedas tienen referencias fijas del 28/09/2026, tomadas una sola vez de
[Frankfurter](https://frankfurter.dev/), calculadas como USD/ARS dividido por
USD/moneda y guardadas con seis decimales. La aplicación no consulta Frankfurter.
Son referencias fijas, no valores actualizados automáticamente ni precios
de compra o venta garantizados.

Al iniciar, se sincronizan esas tasas por código sin reemplazar el catálogo.
La pantalla muestra dos decimales. USD se muestra usando la última cotización
oficial guardada; abrir Monedas no consulta internet.

La opción 13 consulta [DolarAPI](https://dolarapi.com/) y pide confirmación antes
de guardar el valor de venta, con la fecha de actualización informada por la
fuente en horario argentino. Consultar no obliga a guardar.

La opción 14 compara con el catálogo público de [Cúspide](https://cuspide.com/)
por ISBN. Requiere conexión y que el libro esté disponible en el catálogo de
la fuente. No modifica los precios locales ni incluye gastos de envío.

La conversión usa `importe * tasa_origen / tasa_destino`, pasando por ARS y
redondeando a dos decimales. Si interviene USD, pide tipo y fecha y utiliza el
registro guardado para esa combinación. Las otras monedas usan su tasa fija.

Los precios y cotizaciones iniciales son datos de demostración. Los tipos
Simulación A, B y C completan los datos de prueba y no tienen consulta externa.

## Entrega

El archivo solicitado por la consigna es `01_Book_Manager_Grupo_44.ipynb`,
completado sobre la plantilla original y ejecutado sin errores. El repositorio
y esta documentación acompañan ese trabajo; no reemplazan el notebook.
