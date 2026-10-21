from decimal import Decimal

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ValidarCuspidePipeline:
    """Valida y normaliza los datos obtenidos de Cúspide."""

    campos_obligatorios = (
        "libro_id",
        "isbn",
        "titulo_catalogo",
        "precio_interno",
        "moneda_interna",
        "titulo_web",
        "precio_web",
        "url_imagen",
        "descripcion_detallada",
        "url_producto",
        "fecha_extraccion",
    )

    def process_item(self, item):
        datos = ItemAdapter(item)

        faltantes = [
            campo
            for campo in self.campos_obligatorios
            if datos.get(campo) in (None, "")
        ]

        if faltantes:
            raise DropItem(
                "Resultado incompleto; faltan: " + ", ".join(faltantes)
            )

        try:
            precio_interno = Decimal(str(datos["precio_interno"]))
            precio_web = Decimal(str(datos["precio_web"]))
        except Exception as error:
            raise DropItem(f"Precio inválido: {error}") from error

        if precio_interno <= 0 or precio_web <= 0:
            raise DropItem("Los precios deben ser mayores que cero.")

        datos["precio_interno"] = precio_interno
        datos["precio_web"] = precio_web

        formas_pago = datos.get("formas_pago") or []
        datos["formas_pago"] = list(dict.fromkeys(formas_pago))

        return item