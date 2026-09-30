from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from book_manager.services.archivos_json import (
    CARPETA_JSON,
    leer_documento,
    leer_fecha,
    leer_importe,
    leer_registros,
    leer_texto,
)


@dataclass(frozen=True)
class CotizacionArchivo:
    """Representa un valor del dólar leído de un archivo local."""

    tipo_id: int
    nombre: str
    fecha: date
    valor: Decimal
    fuente: str


class LectorCotizacionesJSON:
    """Consulta cotizaciones locales sin modificar los CSV del sistema."""

    def __init__(self, ruta: Path | None = None) -> None:
        self._ruta = (
            Path(ruta) if ruta is not None else CARPETA_JSON / "cotizaciones.json"
        )

    def consultar(self, tipo_id: int) -> CotizacionArchivo:
        """Devuelve la cotización de fecha más reciente para el tipo indicado."""
        if type(tipo_id) is not int or tipo_id <= 0:
            raise ValueError("El identificador del tipo debe ser un entero positivo.")

        documento = leer_documento(self._ruta)
        fuente = leer_texto(documento.get("fuente"), "fuente")
        registros = leer_registros(documento, "cotizaciones")
        claves = set()
        encontradas = []

        for numero, registro in enumerate(registros, start=1):
            identificador = registro.get("tipo_id")
            if type(identificador) is not int or identificador <= 0:
                raise ValueError(
                    f"Cotización {numero}: tipo_id debe ser un entero positivo."
                )
            nombre = leer_texto(registro.get("nombre"), "nombre")
            fecha = leer_fecha(registro.get("fecha"), "fecha")
            valor = leer_importe(registro.get("valor"), "valor")
            clave = (identificador, fecha)
            if clave in claves:
                raise ValueError(
                    "Hay cotizaciones duplicadas para el mismo tipo y fecha."
                )
            claves.add(clave)
            if identificador == tipo_id:
                encontradas.append(
                    CotizacionArchivo(identificador, nombre, fecha, valor, fuente)
                )

        if not encontradas:
            raise ValueError("No hay cotizaciones para ese tipo en el archivo JSON.")
        return max(encontradas, key=lambda cotizacion: cotizacion.fecha)
