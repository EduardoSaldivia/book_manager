import argparse
import csv
from dataclasses import dataclass
from decimal import InvalidOperation
from pathlib import Path
from typing import Any

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


CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_DATOS = CARPETA_PROYECTO / "data"


@dataclass
class Aplicacion:
    """Agrupa los componentes preparados para utilizar el sistema."""

    servicios: dict[str, Any]
    consola: Consola
    precarga: PrecargaDatos
    carpeta_datos: Path


def crear_aplicacion(
    carpeta_datos: Path | None = None,
) -> Aplicacion:
    """Construye los componentes sin cargar datos ni abrir el menú."""
    carpeta = (
        Path(carpeta_datos)
        if carpeta_datos is not None
        else CARPETA_DATOS
    )
    carpeta.mkdir(parents=True, exist_ok=True)

    repo_generos = RepositorioGenero(
        str(carpeta / "generos.csv")
    )
    repo_editoriales = RepositorioEditorial(
        str(carpeta / "editoriales.csv")
    )
    repo_monedas = RepositorioMoneda(
        str(carpeta / "monedas.csv")
    )
    repo_tipos = RepositorioTipoCotizacion(
        str(carpeta / "tipos_cotizacion.csv")
    )

    repo_libros = RepositorioLibro(
        str(carpeta / "libros.csv"),
        repo_editoriales,
        repo_generos,
    )
    repo_precios = RepositorioPrecio(
        str(carpeta / "precios.csv"),
        repo_libros,
        repo_monedas,
    )
    repo_stock = RepositorioStock(
        str(carpeta / "stock.csv"),
        repo_libros,
    )
    repo_cotizaciones = RepositorioCotizacionDolar(
        str(carpeta / "cotizaciones.csv"),
        repo_tipos,
    )

    servicios = {
        "generos": ServicioGenero(
            repo_generos,
            repo_libros,
        ),
        "editoriales": ServicioEditorial(
            repo_editoriales,
            repo_libros,
        ),
        "monedas": ServicioMoneda(
            repo_monedas,
            repo_precios,
        ),
        "tipos": ServicioTipoCotizacion(
            repo_tipos,
            repo_cotizaciones,
        ),
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
        "stock": ServicioStock(
            repo_stock,
            repo_libros,
        ),
        "cotizaciones": ServicioCotizacionDolar(
            repo_cotizaciones,
            repo_tipos,
        ),
    }

    consola = Consola(**servicios)
    precarga = PrecargaDatos(**servicios)

    return Aplicacion(
        servicios=servicios,
        consola=consola,
        precarga=precarga,
        carpeta_datos=carpeta,
    )


def main(
    import_default_data: bool = False,
    interactivo: bool = True,
    carpeta_datos: Path | None = None,
) -> Aplicacion:
    """Prepara el sistema y ejecuta las acciones solicitadas."""
    aplicacion = crear_aplicacion(carpeta_datos)

    if import_default_data:
        resumen = aplicacion.precarga.cargar()

        print("\n--- PRECARGA DE DATOS DE DEMOSTRACIÓN ---")

        for nombre, cantidad in resumen.items():
            print(f"{nombre}: {cantidad} registro(s) agregado(s)")

    else:
        aplicacion.precarga.sincronizar_cotizaciones_fijas()

    if interactivo:
        aplicacion.consola.ejecutar()

    return aplicacion


def ejecutar_desde_terminal() -> None:
    """Interpreta las opciones de ejecución desde la terminal."""
    parser = argparse.ArgumentParser(
        description="Book Manager - Gestión de una librería."
    )
    parser.add_argument(
        "--precargar",
        action="store_true",
        help="Agrega los registros iniciales que todavía no existen.",
    )
    parser.add_argument(
        "--sin-menu",
        action="store_true",
        help="Prepara el sistema y termina sin abrir el menú.",
    )
    parser.add_argument(
        "--datos",
        type=Path,
        default=CARPETA_DATOS,
        help="Carpeta donde se guardan los datos de funcionamiento.",
    )

    argumentos = parser.parse_args()

    primera_ejecucion = not any(
        (argumentos.datos / nombre).exists()
        for nombre in PrecargaDatos.ARCHIVOS
    )

    try:
        main(
            import_default_data=(
                argumentos.precargar or primera_ejecucion
            ),
            interactivo=not argumentos.sin_menu,
            carpeta_datos=argumentos.datos,
        )
    except (
        ValueError,
        InvalidOperation,
        OSError,
        csv.Error,
        KeyError,
    ) as error:
        parser.exit(
            status=1,
            message=f"No se pudo iniciar Book Manager: {error}\n",
        )


if __name__ == "__main__":
    ejecutar_desde_terminal()