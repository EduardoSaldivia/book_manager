import re
from decimal import Decimal

from scrapy.loader import ItemLoader
from itemloaders.processors import Identity, MapCompose, TakeFirst

from .items import CuspideScraperItem


def limpiar_texto(valor):
    """Quita espacios repetidos y símbolos sobrantes al inicio o al final."""
    if valor is None:
        return ""

    texto = str(valor).replace("\xa0", " ")
    texto = " ".join(texto.split())
    return texto.strip(" >\t\r\n")


def convertir_precio(valor):
    """Convierte un precio argentino, como $ 38.900,00, a Decimal."""
    if isinstance(valor, Decimal):
        return valor

    texto = limpiar_texto(valor)
    texto = re.sub(r"[^\d,.\-]", "", texto)

    if not texto:
        raise ValueError(f"No se pudo interpretar el precio: {valor!r}")

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return Decimal(texto)


class CuspideItemLoader(ItemLoader):
    default_item_class = CuspideScraperItem
    default_input_processor = MapCompose(limpiar_texto)
    default_output_processor = TakeFirst()

    precio_interno_in = MapCompose(convertir_precio)
    precio_web_in = MapCompose(convertir_precio)

    formas_pago_out = Identity()