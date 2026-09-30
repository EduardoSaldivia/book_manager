from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import requests


@dataclass(frozen=True)
class CotizacionExterna:
    """Representa una cotización recibida desde DolarAPI."""

    casa: str
    nombre: str
    compra: Decimal
    venta: Decimal
    actualizada: datetime


class ClienteDolarAPI:
    """Consulta y valida las cotizaciones publicadas por DolarAPI."""

    URL_BASE = "https://dolarapi.com/v1/dolares"

    CASAS = {
        "oficial",
        "blue",
        "bolsa",
        "contadoconliqui",
        "tarjeta",
        "mayorista",
        "cripto",
    }

    @staticmethod
    def _validar_importe(valor: object) -> Decimal:
        """Comprueba que el importe sea numérico, finito y positivo."""
        if isinstance(valor, bool) or not isinstance(
            valor, (int, Decimal)
        ):
            raise ValueError("La API devolvió un importe no numérico.")

        importe = Decimal(valor)

        if not importe.is_finite() or importe <= 0:
            raise ValueError("La API devolvió un importe inválido.")

        return importe

    def consultar(self, casa: str = "oficial") -> CotizacionExterna:
        """Obtiene la última cotización publicada para un tipo."""
        casa = casa.strip().lower()

        if casa not in self.CASAS:
            raise ValueError("El tipo solicitado no está disponible.")

        try:
            respuesta = requests.get(
                f"{self.URL_BASE}/{casa}",
                timeout=(5, 10),
            )
            respuesta.raise_for_status()
        except requests.RequestException as error:
            raise ValueError(
                "No se pudo consultar DolarAPI. "
                "Revisá la conexión e intentá nuevamente."
            ) from error

        try:
            datos = respuesta.json(parse_float=Decimal)
        except ValueError as error:
            raise ValueError(
                "DolarAPI no devolvió una respuesta JSON válida."
            ) from error

        if not isinstance(datos, dict):
            raise ValueError("La respuesta de DolarAPI no es válida.")

        if datos.get("moneda") != "USD":
            raise ValueError("La cotización recibida no corresponde a USD.")

        if datos.get("casa") != casa:
            raise ValueError("La API devolvió otro tipo de cotización.")

        nombre = datos.get("nombre")
        fecha_texto = datos.get("fechaActualizacion")

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("La cotización recibida no tiene nombre.")

        if not isinstance(fecha_texto, str):
            raise ValueError("La cotización recibida no tiene fecha.")

        try:
            actualizada = datetime.fromisoformat(
                fecha_texto.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise ValueError(
                "La fecha recibida desde DolarAPI no es válida."
            ) from error

        if actualizada.tzinfo is None:
            raise ValueError("La fecha recibida no indica zona horaria.")

        return CotizacionExterna(
            casa=casa,
            nombre=nombre.strip(),
            compra=self._validar_importe(datos.get("compra")),
            venta=self._validar_importe(datos.get("venta")),
            actualizada=actualizada,
        )