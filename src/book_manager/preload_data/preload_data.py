import csv
from pathlib import Path
from typing import TypeVar
from decimal import Decimal

from book_manager.entities.entities import EntidadBase, Moneda
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
    ServicioBase,
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)


T = TypeVar("T", bound=EntidadBase)


class PrecargaDatos:
    """Importa datos iniciales sin reemplazar registros existentes."""

    ARCHIVOS = {
        "generos.csv": ["id", "nombre"],
        "editoriales.csv": ["id", "nombre"],
        "monedas.csv": ["id", "codigo", "nombre", "cotizacion_ars"],
        "tipos_cotizacion.csv": ["id", "nombre"],
        "libros.csv": [
            "id",
            "isbn",
            "titulo",
            "autor",
            "editorial_id",
            "genero_id",
        ],
        "precios.csv": ["id", "libro_id", "moneda_id", "importe"],
        "stock.csv": ["libro_id", "cantidad"],
        "cotizaciones.csv": ["tipo_id", "fecha", "valor"],
    }

    def __init__(
        self,
        generos: ServicioGenero,
        editoriales: ServicioEditorial,
        monedas: ServicioMoneda,
        tipos: ServicioTipoCotizacion,
        libros: ServicioLibro,
        precios: ServicioPrecio,
        stock: ServicioStock,
        cotizaciones: ServicioCotizacionDolar,
        carpeta: Path | None = None,
    ) -> None:
        self._generos = generos
        self._editoriales = editoriales
        self._monedas = monedas
        self._tipos = tipos
        self._libros = libros
        self._precios = precios
        self._stock = stock
        self._cotizaciones = cotizaciones

        if carpeta is None:
            carpeta = (
                Path(__file__).resolve().parents[1]
                / "migrations"
                / "csv"
            )

        self._carpeta = Path(carpeta)

    def _ruta(self, nombre: str) -> str:
        """Construye la ruta de un archivo de datos iniciales."""
        return str(self._carpeta / nombre)

    def _comprobar_archivos(self) -> None:
        """Comprueba archivos, encabezados y cantidad mínima de filas."""
        for nombre, columnas in self.ARCHIVOS.items():
            ruta = self._carpeta / nombre

            if not ruta.is_file():
                raise FileNotFoundError(
                    f"Falta el archivo de precarga: {ruta}"
                )

            with ruta.open(
                mode="r",
                encoding="utf-8",
                newline="",
            ) as archivo:
                lector = csv.DictReader(archivo)

                if lector.fieldnames != columnas:
                    raise ValueError(
                        f"Encabezado incorrecto en {nombre}. "
                        f"Se esperaba: {','.join(columnas)}"
                    )

                filas = list(lector)

            if len(filas) < 10:
                raise ValueError(
                    f"{nombre} debe contener al menos diez registros."
                )

            for numero, fila in enumerate(filas, start=2):
                if None in fila or any(
                    valor is None or (
                        not valor.strip()
                        and not (
                            nombre == "monedas.csv"
                            and columna == "cotizacion_ars"
                            and fila.get("codigo", "").strip().upper() == "USD"
                        )
                    )
                    for columna, valor in fila.items()
                ):
                    raise ValueError(
                        f"Datos incompletos o columnas incorrectas "
                        f"en {nombre}, registro {numero}."
                    )

    def _leer_monedas_iniciales(self) -> list[Moneda]:
        """Valida las tasas fijas del CSV antes de sincronizar valores."""
        ruta = Path(self._ruta("monedas.csv"))
        with ruta.open(encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames != self.ARCHIVOS["monedas.csv"]:
                raise ValueError(
                    "monedas.csv debe tener: id,codigo,nombre,cotizacion_ars"
                )
            filas = list(lector)
            if any(None in fila or None in fila.values() for fila in filas):
                raise ValueError("Hay columnas incompletas en monedas.csv.")
        monedas = RepositorioMoneda(str(ruta)).leer_todos()
        codigos = set()
        identificadores = set()
        for moneda in monedas:
            if moneda.codigo in codigos or moneda.id in identificadores:
                raise ValueError("Hay códigos o identificadores repetidos en monedas.csv.")
            codigos.add(moneda.codigo)
            identificadores.add(moneda.id)
            if moneda.codigo == "USD":
                if moneda.cotizacion_ars is not None:
                    raise ValueError("USD debe dejar cotizacion_ars vacía; usa su histórico.")
            elif moneda.codigo == "ARS":
                if moneda.cotizacion_ars != Decimal("1"):
                    raise ValueError("La cotización fija de ARS debe ser 1.")
            elif moneda.cotizacion_ars is None:
                raise ValueError(f"Falta cotizacion_ars para {moneda.codigo}.")
        return monedas

    def sincronizar_cotizaciones_fijas(self) -> int:
        """Actualiza solo tasas, por código, conservando IDs y nombres locales."""
        tasas = {
            moneda.codigo: moneda.cotizacion_ars
            for moneda in self._leer_monedas_iniciales()
        }
        actualizadas = 0
        for actual in self._monedas.leer_todos():
            if actual.codigo not in tasas:
                continue
            valor = tasas[actual.codigo]
            if actual.cotizacion_ars != valor:
                nueva = Moneda(actual.id, actual.codigo, actual.nombre, valor)
                self._monedas.actualizar(nueva)
                actualizadas += 1
        return actualizadas

    def _cargar_con_id(
        self,
        entidades: list[T],
        servicio: ServicioBase[T],
    ) -> int:
        """Crea solamente las entidades cuyo identificador no existe."""
        creadas = 0

        for entidad in entidades:
            existente = servicio.leer_por_id(entidad.id)

            if existente is None:
                servicio.crear(entidad)
                creadas += 1

        return creadas

    def cargar(self) -> dict[str, int]:
        """Carga las ocho entidades y devuelve los registros agregados."""
        self._comprobar_archivos()

        fuente_generos = RepositorioGenero(
            self._ruta("generos.csv")
        )
        fuente_editoriales = RepositorioEditorial(
            self._ruta("editoriales.csv")
        )
        fuente_monedas = RepositorioMoneda(
            self._ruta("monedas.csv")
        )
        fuente_tipos = RepositorioTipoCotizacion(
            self._ruta("tipos_cotizacion.csv")
        )

        fuente_libros = RepositorioLibro(
            self._ruta("libros.csv"),
            fuente_editoriales,
            fuente_generos,
        )
        fuente_precios = RepositorioPrecio(
            self._ruta("precios.csv"),
            fuente_libros,
            fuente_monedas,
        )
        fuente_stock = RepositorioStock(
            self._ruta("stock.csv"),
            fuente_libros,
        )
        fuente_cotizaciones = RepositorioCotizacionDolar(
            self._ruta("cotizaciones.csv"),
            fuente_tipos,
        )

        datos_generos = fuente_generos.leer_todos()
        datos_editoriales = fuente_editoriales.leer_todos()
        datos_monedas = self._leer_monedas_iniciales()
        datos_tipos = fuente_tipos.leer_todos()
        datos_libros = fuente_libros.leer_todos()
        datos_precios = fuente_precios.leer_todos()
        datos_stock = fuente_stock.leer_todos()
        datos_cotizaciones = fuente_cotizaciones.leer_todos()

        resumen = {}

        resumen["generos"] = self._cargar_con_id(
            datos_generos, self._generos
        )
        resumen["editoriales"] = self._cargar_con_id(
            datos_editoriales, self._editoriales
        )
        resumen["monedas"] = self._cargar_con_id(
            datos_monedas, self._monedas
        )
        resumen["tipos_cotizacion"] = self._cargar_con_id(
            datos_tipos, self._tipos
        )
        resumen["libros"] = self._cargar_con_id(
            datos_libros, self._libros
        )
        resumen["precios"] = self._cargar_con_id(
            datos_precios, self._precios
        )

        resumen["stock"] = 0

        for registro in datos_stock:
            existente = self._stock.leer_por_libro(
                registro.libro.id
            )

            if existente is None:
                self._stock.crear(registro)
                resumen["stock"] += 1

        resumen["cotizaciones"] = 0

        for cotizacion in datos_cotizaciones:
            existente = self._cotizaciones.leer_por_tipo_y_fecha(
                cotizacion.tipo.id,
                cotizacion.fecha,
            )

            if existente is None:
                self._cotizaciones.crear(cotizacion)
                resumen["cotizaciones"] += 1

        self.sincronizar_cotizaciones_fijas()
        return resumen