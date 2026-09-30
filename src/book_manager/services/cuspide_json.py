import re
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
class LibroReferencia:
    """Representa un libro del catálogo de comparación guardado en JSON."""

    isbn: str
    titulo: str
    precio: Decimal
    moneda: str
    disponible: bool | None
    actualizada: date
    fuente: str


def normalizar_isbn(valor: object) -> str:
    """Elimina separadores y exige los trece dígitos usados por el catálogo."""
    isbn = leer_texto(valor, "isbn").replace("-", "").replace(" ", "")
    if re.fullmatch(r"[0-9]{13}", isbn) is None:
        raise ValueError("El ISBN debe contener 13 dígitos.")
    return isbn


class LectorCuspideJSON:
    """Lee el archivo de referencia local; no se conecta al sitio de Cúspide."""

    def __init__(self, ruta: Path | None = None) -> None:
        self._ruta = (
            Path(ruta)
            if ruta is not None
            else CARPETA_JSON / "precios_cuspide.json"
        )

    def consultar_por_isbn(self, isbn: str) -> LibroReferencia | None:
        """Valida el catálogo completo y devuelve el libro solicitado si existe."""
        buscado = normalizar_isbn(isbn)
        documento = leer_documento(self._ruta)
        fuente = leer_texto(documento.get("fuente"), "fuente")
        actualizada = leer_fecha(
            documento.get("fecha_actualizacion"), "fecha_actualizacion"
        )
        registros = leer_registros(documento, "libros")
        identificadores = set()
        encontrado = None

        for registro in registros:
            identificador = normalizar_isbn(registro.get("isbn"))
            if identificador in identificadores:
                raise ValueError("Hay libros con ISBN duplicado en el catálogo JSON.")
            identificadores.add(identificador)
            titulo = leer_texto(registro.get("titulo"), "titulo")
            precio = leer_importe(registro.get("precio"), "precio")
            moneda = leer_texto(registro.get("moneda"), "moneda").upper()
            if moneda != "ARS":
                raise ValueError("Los precios del catálogo JSON deben estar en ARS.")
            disponible = registro.get("disponible")
            if disponible is not None and type(disponible) is not bool:
                raise ValueError("El campo 'disponible' debe ser true, false o null.")
            if identificador == buscado:
                encontrado = LibroReferencia(
                    identificador, titulo, precio, moneda,
                    disponible, actualizada, fuente,
                )

        return encontrado
