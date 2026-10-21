"""Migración explícita de los ocho CSV del Sprint 1 a PostgreSQL."""
import argparse
import csv
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    GeneroModelo, EditorialModelo, MonedaModelo, TipoCotizacionModelo,
    LibroModelo, PrecioModelo, StockModelo, CotizacionDolarModelo,
)

MODELOS = (
    GeneroModelo, EditorialModelo, MonedaModelo, TipoCotizacionModelo,
    LibroModelo, PrecioModelo, StockModelo, CotizacionDolarModelo,
)
CARPETA = Path(__file__).resolve().parent


def leer_csvs(carpeta_csvs: str) -> dict[str, list[dict]]:
    """Valida todos los archivos antes de modificar la base de datos."""
    datos = {}
    for modelo in MODELOS:
        tabla = modelo.__table__
        ruta = Path(carpeta_csvs) / f"{tabla.name}.csv"
        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames != list(tabla.columns.keys()):
                raise ValueError(f"Encabezado incorrecto en {ruta.name}.")
            registros = []
            claves = set()
            for numero, fila in enumerate(lector, 2):
                try:
                    if None in fila or None in fila.values():
                        raise ValueError("Cantidad de columnas incorrecta.")
                    registro = {}
                    for columna in tabla.columns:
                        texto = fila[columna.name].strip()
                        tipo = columna.type.python_type
                        if not texto:
                            if not columna.nullable:
                                raise ValueError(f"Falta {columna.name}.")
                            valor = None
                        elif tipo is date:
                            valor = date.fromisoformat(texto)
                        elif tipo is Decimal:
                            valor = Decimal(texto)
                            if not valor.is_finite() or valor < 0:
                                raise ValueError("Importe no válido.")
                            if columna.name != "importe" and valor == 0:
                                raise ValueError("La cotización debe ser positiva.")
                            escala = columna.type.scale
                            if valor != valor.quantize(Decimal(1).scaleb(-escala)):
                                raise ValueError(f"{columna.name}: demasiados decimales.")
                            if valor >= Decimal(10) ** (columna.type.precision - escala):
                                raise ValueError("Importe fuera del rango admitido.")
                        elif tipo is int:
                            valor = int(texto)
                            minimo = 0 if columna.name == "cantidad" else 1
                            if not minimo <= valor <= 2147483647:
                                raise ValueError("Entero fuera del rango admitido.")
                        else:
                            valor = texto
                        registro[columna.name] = valor
                    if tabla.name == "monedas":
                        codigo = registro["codigo"]
                        if not re.fullmatch(r"[A-Z]{3}", codigo):
                            raise ValueError("Código de moneda no válido.")
                        tasa = registro["cotizacion_ars"]
                        if codigo == "ARS" and tasa != Decimal("1"):
                            raise ValueError("ARS debe tener cotización 1.")
                        if codigo == "USD" and tasa is not None:
                            raise ValueError("USD utiliza su histórico; dejar tasa fija vacía.")
                        if codigo not in {"ARS", "USD"} and tasa is None:
                            raise ValueError("Falta la tasa fija de la moneda.")
                    clave = tuple(registro[c.name] for c in tabla.primary_key.columns)
                    if clave in claves:
                        raise ValueError("Clave primaria repetida.")
                    claves.add(clave)
                    registros.append(registro)
                except (ValueError, InvalidOperation) as error:
                    raise ValueError(f"{ruta.name}, fila {numero}: {error}") from error
        datos[tabla.name] = registros

    # Comprueba referencias y valores únicos dentro del conjunto de origen.
    for modelo in MODELOS:
        tabla = modelo.__table__
        for columna in tabla.columns:
            if columna.unique:
                valores = [r[columna.name] for r in datos[tabla.name]]
                if len(valores) != len(set(valores)):
                    raise ValueError(f"Valores repetidos: {tabla.name}.{columna.name}.")
            for fk in columna.foreign_keys:
                destino = fk.column
                permitidos = {r[destino.name] for r in datos[destino.table.name]}
                if any(r[columna.name] not in permitidos for r in datos[tabla.name]):
                    raise ValueError(f"Referencia inexistente: {tabla.name}.{columna.name}.")
    return datos


def generar_sql(datos: dict, carpeta_sqls: str) -> list[Path]:
    """Genera una copia SQL del origen, ordenada por dependencias."""
    carpeta = Path(carpeta_sqls)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for numero, modelo in enumerate(MODELOS, 1):
        tabla = modelo.__table__
        lineas = ["-- Datos de origen del Sprint 1. Ejecutar archivos en orden.",
                  "-- Las claves existentes se conservan sin reemplazar.", "BEGIN;"]
        for fila in datos[tabla.name]:
            sentencia = insert(tabla).values(**fila).on_conflict_do_nothing(
                index_elements=list(tabla.primary_key.columns)
            )
            lineas.append(str(sentencia.compile(
                dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
            )) + ";")
        lineas.append("COMMIT;")
        ruta = carpeta / f"{numero:02d}_{tabla.name}.sql"
        temporal = ruta.with_suffix(".sql.tmp")
        temporal.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        temporal.replace(ruta)
        rutas.append(ruta)
    return rutas


def migrar_datos(carpeta_csvs: str, carpeta_sqls: str,
                 conexion: ConexionDB | None = None) -> dict:
    """Genera SQL e importa todos los CSV en una sola transacción.

    Repetir la migración no duplica claves ni reemplaza datos existentes.
    Los SQL describen el origen; su existencia no confirma una carga exitosa.
    """
    datos = leer_csvs(carpeta_csvs)
    generar_sql(datos, carpeta_sqls)
    propia = conexion is None
    db = conexion if conexion is not None else ConexionDB()
    resumen = {}
    try:
        with db.transaccion() as sesion:
            for modelo in MODELOS:
                tabla = modelo.__table__
                agregados = 0
                for fila in datos[tabla.name]:
                    sentencia = insert(tabla).values(**fila).on_conflict_do_nothing(
                        index_elements=list(tabla.primary_key.columns)
                    ).returning(*tabla.primary_key.columns)
                    if sesion.execute(sentencia).first() is not None:
                        agregados += 1
                resumen[tabla.name] = {
                    "agregados": agregados,
                    "conservados": len(datos[tabla.name]) - agregados,
                    "total": sesion.scalar(select(func.count()).select_from(modelo)),
                }
        return resumen
    finally:
        if propia:
            db.cerrar()

def cargar_datos_desde_sql(
    carpeta_sqls: str,
    conexion: ConexionDB | None = None,
) -> list[str]:
    """Ejecuta en orden los archivos SQL de una carpeta."""
    carpeta = Path(carpeta_sqls)

    if not carpeta.is_dir():
        raise FileNotFoundError(f"No existe la carpeta SQL: {carpeta}")

    rutas = sorted(carpeta.glob("*.sql"))
    if not rutas:
        raise FileNotFoundError(f"No hay archivos .sql en: {carpeta}")

    propia = conexion is None
    db = conexion if conexion is not None else ConexionDB()
    cargados = []

    try:
        for ruta in rutas:
            contenido = ruta.read_text(encoding="utf-8").strip()
            if not contenido:
                raise ValueError(f"El archivo está vacío: {ruta.name}")

            # Los SQL generados tienen varias sentencias y manejan su
            # propia transacción con BEGIN y COMMIT.
            raw = db.engine.raw_connection()
            try:
                cursor = raw.cursor()
                try:
                    cursor.execute(contenido, prepare=False)
                finally:
                    cursor.close()
            finally:
                raw.close()

            cargados.append(ruta.name)

        return cargados
    finally:
        if propia:
            db.cerrar()


def ejecutar() -> None:
    parser = argparse.ArgumentParser(description="Migración del Sprint 1 a PostgreSQL.")
    parser.add_argument("--csv", type=Path, default=CARPETA / "csv")
    parser.add_argument("--sql", type=Path, default=CARPETA / "sql")
    parser.add_argument("--solo-sql", action="store_true",
                        help="Valida y genera SQL sin conectarse a Supabase.")
    args = parser.parse_args()
    try:
        if args.solo_sql:
            datos = leer_csvs(str(args.csv))
            for ruta in generar_sql(datos, str(args.sql)):
                print(f"Generado: {ruta.name}")
            print("Validación local completa. No se modificó Supabase.")
        else:
            resumen = migrar_datos(str(args.csv), str(args.sql))
            for tabla, resultado in resumen.items():
                print(f"{tabla}: {resultado}")
            print("Migración confirmada.")
    except SQLAlchemyError:
        parser.exit(1, "No se completó la migración. Revisá la conexión, las tablas y las restricciones.\n")
    except (ValueError, OSError, csv.Error) as error:
        parser.exit(1, f"No se completó la migración: {error}\n")


if __name__ == "__main__":
    ejecutar()