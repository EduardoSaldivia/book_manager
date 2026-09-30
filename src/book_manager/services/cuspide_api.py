import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from html import unescape

import requests


@dataclass(frozen=True)
class LibroExterno:
    """Representa un libro consultado en Cúspide."""

    isbn: str
    titulo: str
    precio: Decimal
    moneda: str
    disponible: bool
    url: str
    consultado: datetime


class ClienteCuspideAPI:
    """Consulta el catálogo público de Cúspide por ISBN."""

    URL = "https://cuspide.com/wp-json/wc/store/v1/products"

    def consultar_por_isbn(self, isbn: str) -> LibroExterno | None:
        """Devuelve el libro encontrado o None si no hay resultados."""
        isbn = isbn.strip().replace("-", "").replace(" ", "")

        if re.fullmatch(r"[0-9]{13}", isbn) is None:
            raise ValueError(
                "Para esta consulta ingresá un ISBN de 13 dígitos."
            )

        try:
            respuesta = requests.get(
                self.URL,
                params={"sku": isbn, "per_page": 2},
                timeout=(5, 15),
            )
            respuesta.raise_for_status()
        except requests.RequestException as error:
            raise ValueError(
                "No se pudo consultar Cúspide. "
                "Revisá la conexión e intentá nuevamente."
            ) from error

        try:
            productos = respuesta.json()
        except ValueError as error:
            raise ValueError(
                "Cúspide no devolvió una respuesta JSON válida."
            ) from error

        if not isinstance(productos, list):
            raise ValueError("La respuesta de Cúspide no es válida.")

        if not productos:
            return None

        if len(productos) != 1:
            raise ValueError(
                "Cúspide devolvió varios productos para el mismo ISBN."
            )

        producto = productos[0]

        if not isinstance(producto, dict):
            raise ValueError("El producto recibido no es válido.")

        if producto.get("sku") != isbn:
            raise ValueError(
                "El ISBN recibido no coincide con el solicitado."
            )

        titulo = producto.get("name")
        url = producto.get("permalink")
        disponible = producto.get("is_in_stock")
        precios = producto.get("prices")

        if not isinstance(titulo, str) or not titulo.strip():
            raise ValueError("El producto no tiene un título válido.")

        if not isinstance(url, str) or not url.strip():
            raise ValueError("El producto no tiene un enlace válido.")

        if not isinstance(disponible, bool):
            raise ValueError("No se pudo determinar la disponibilidad.")

        if not isinstance(precios, dict):
            raise ValueError("El producto no tiene información de precio.")

        if precios.get("currency_code") != "ARS":
            raise ValueError("El precio recibido no está expresado en ARS.")

        importe_texto = precios.get("price")
        decimales = precios.get("currency_minor_unit")

        if (
            not isinstance(importe_texto, str)
            or re.fullmatch(r"[0-9]+", importe_texto) is None
        ):
            raise ValueError("El producto no tiene un precio válido.")

        if type(decimales) is not int or not 0 <= decimales <= 6:
            raise ValueError("La escala del precio recibido no es válida.")

        importe = Decimal(importe_texto) / (Decimal(10) ** decimales)

        if importe <= 0:
            raise ValueError("El producto no tiene un precio positivo.")

        return LibroExterno(
            isbn=isbn,
            titulo=unescape(titulo.strip()),
            precio=importe,
            moneda="ARS",
            disponible=disponible,
            url=url,
            consultado=datetime.now(timezone.utc),
        )