import argparse
from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from book_manager.database.connection import ConexionDB
from book_manager.preload_data.preload_data import PrecargaDatos
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar,
    RepositorioEditorial,
    RepositorioGenero,
    RepositorioLibro,
    RepositorioMoneda,
    RepositorioPrecio,
    RepositorioStock,
    RepositorioTipoCotizacion,
)
from book_manager.services.auditoria import ServicioAuditoria
from book_manager.services.scraping import ServicioScraping
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)
from book_manager.ui.console import Consola


@dataclass
class Aplicacion:
    servicios: dict[str, Any]
    consola: Consola
    precarga: PrecargaDatos
    conexion: ConexionDB


def crear_aplicacion(
    conexion: ConexionDB | None = None,
) -> Aplicacion:
    """Construye el sistema usando repositorios SQLAlchemy."""
    db = conexion if conexion is not None else ConexionDB()

    repo_generos = RepositorioGenero(db)
    repo_editoriales = RepositorioEditorial(db)
    repo_monedas = RepositorioMoneda(db)
    repo_tipos = RepositorioTipoCotizacion(db)
    repo_libros = RepositorioLibro(db)
    repo_precios = RepositorioPrecio(db)
    repo_stock = RepositorioStock(db)
    repo_cotizaciones = RepositorioCotizacionDolar(db)

    servicios = {
        "generos": ServicioGenero(repo_generos, repo_libros),
        "editoriales": ServicioEditorial(repo_editoriales, repo_libros),
        "monedas": ServicioMoneda(repo_monedas, repo_precios),
        "tipos": ServicioTipoCotizacion(repo_tipos, repo_cotizaciones),
        "libros": ServicioLibro(
            repo_libros,
            repo_editoriales,
            repo_generos,
            repo_precios,
            repo_stock,
        ),
        "precios": ServicioPrecio(
            repo_precios,
            repo_libros,
            repo_monedas,
            repo_cotizaciones,
        ),
        "stock": ServicioStock(repo_stock, repo_libros),
        "cotizaciones": ServicioCotizacionDolar(
            repo_cotizaciones,
            repo_tipos,
        ),
    }

    consola = Consola(
        **servicios,
        scraping=ServicioScraping(),
        auditoria=ServicioAuditoria(db),
    )

    return Aplicacion(
        servicios=servicios,
        consola=consola,
        precarga=PrecargaDatos(db),
        conexion=db,
    )


def main(interactivo: bool = True) -> None:
    """Inicia el menú o muestra un resumen de los registros."""
    db = ConexionDB()

    try:
        db.probar_conexion()
        aplicacion = crear_aplicacion(db)

        if interactivo:
            aplicacion.consola.ejecutar()
        else:
            for nombre, servicio in aplicacion.servicios.items():
                cantidad = len(servicio.leer_todos())
                print(f"{nombre}: {cantidad} registro(s)")
    finally:
        db.cerrar()


def ejecutar_desde_terminal() -> None:
    parser = argparse.ArgumentParser(
        description="Book Manager - Sprint 3 - Supabase"
    )
    parser.add_argument(
        "--sin-menu",
        action="store_true",
        help="Comprueba la conexión y muestra los conteos de la base.",
    )
    args = parser.parse_args()

    try:
        main(interactivo=not args.sin_menu)
    except SQLAlchemyError:
        parser.exit(
            1,
            "No se pudo iniciar: revisá conexión y tablas de Supabase.\n",
        )
    except (ValueError, OSError) as error:
        parser.exit(
            1,
            f"No se pudo iniciar Book Manager: {error}\n",
        )


if __name__ == "__main__":
    ejecutar_desde_terminal()
