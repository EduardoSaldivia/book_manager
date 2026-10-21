import re
from datetime import datetime, timezone
from urllib.parse import urlencode

import scrapy

from book_manager.database.connection import ConexionDB
from book_manager.repositories.repositories import (
    RepositorioLibro,
    RepositorioPrecio,
)
from cuspide_scraper.loaders import CuspideItemLoader


class CuspideSpider(scrapy.Spider):
    name = "cuspide"
    allowed_domains = ["cuspide.com"]

    def __init__(self, isbn=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isbn_filtro = (
            self._normalizar_isbn(isbn) if isbn else None
        )

    async def start(self):
        """Carga el catálogo y busca únicamente sus libros."""
        conexion = ConexionDB()

        try:
            libros = RepositorioLibro(conexion).leer_todos()
            precios = RepositorioPrecio(conexion).leer_todos()
        finally:
            conexion.cerrar()

        # Comparamos con Cúspide usando precios internos en ARS.
        precios_ars = {}
        for precio in precios:
            if precio.moneda.codigo == "ARS":
                precios_ars.setdefault(precio.libro.id, precio)

        for libro in libros:
            # Permite probar un solo libro pasando su ISBN por consola.
            if (
                self.isbn_filtro
                and self._normalizar_isbn(libro.isbn) != self.isbn_filtro
            ):
                continue

            precio = precios_ars.get(libro.id)

            if precio is None:
                self.logger.warning(
                    "Se omite %s: no tiene un precio interno en ARS.",
                    libro.titulo,
                )
                continue

            parametros = urlencode({
                "s": libro.titulo,
                "post_type": "product",
            })
            url_busqueda = f"https://cuspide.com/?{parametros}"

            yield scrapy.Request(
                url_busqueda,
                callback=self.parse_busqueda,
                cb_kwargs={"libro": libro, "precio": precio},
            )

    def parse_busqueda(self, response, libro, precio):
        """Visita como máximo los primeros diez resultados del título."""
        tarjetas = response.css("div.product-small")[:10]
        urls_visitadas = set()

        for tarjeta in tarjetas:
            url_producto = tarjeta.css(
                "a.woocommerce-loop-product__link::attr(href)"
            ).get()

            if not url_producto or url_producto in urls_visitadas:
                continue

            urls_visitadas.add(url_producto)

            yield response.follow(
                url_producto,
                callback=self.parse_producto,
                cb_kwargs={"libro": libro, "precio": precio},
            )

    def parse_producto(self, response, libro, precio):
        """Extrae el producto solo si coincide el ISBN del catálogo."""
        isbn_web = response.css(".livriz-code::text").get()

        if (
            not isbn_web
            or self._normalizar_isbn(isbn_web)
            != self._normalizar_isbn(libro.isbn)
        ):
            self.logger.debug(
                "Se descarta un resultado de Cúspide: "
                "no coincide el ISBN para %s.",
                libro.titulo,
            )
            return

        precio_web = response.css(
            ".product-info p.product-page-price "
            ".woocommerce-Price-amount bdi"
        ).xpath("string(.)").get()

        imagen = response.css("img.wp-post-image::attr(src)").get()

        formas_pago = response.xpath(
            "//li[contains(., 'Tarjetas de créditos')]/../li//text()"
        ).getall()

        loader = CuspideItemLoader(response=response)
        loader.add_value("libro_id", libro.id)
        loader.add_value("isbn", libro.isbn)
        loader.add_value("titulo_catalogo", libro.titulo)
        loader.add_value("precio_interno", precio.importe)
        loader.add_value("moneda_interna", precio.moneda.codigo)

        loader.add_css("titulo_web", "h1.product_title::text")
        loader.add_value("precio_web", precio_web)
        loader.add_value(
            "url_imagen",
            response.urljoin(imagen) if imagen else "",
        )
        loader.add_value("formas_pago", formas_pago)
        loader.add_css(
            "descripcion_detallada",
            ".livriz-text-synopsis::text",
        )
        loader.add_value("url_producto", response.url)
        loader.add_value(
            "fecha_extraccion",
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

        yield loader.load_item()

    @staticmethod
    def _normalizar_isbn(isbn):
        """Ignora espacios y guiones al comparar los ISBN."""
        return re.sub(r"[^0-9Xx]", "", isbn).upper()