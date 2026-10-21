import scrapy


class CuspideScraperItem(scrapy.Item):
    # Datos del libro de nuestro catálogo.
    libro_id = scrapy.Field()
    isbn = scrapy.Field()
    titulo_catalogo = scrapy.Field()
    precio_interno = scrapy.Field()
    moneda_interna = scrapy.Field()

    # Datos obtenidos de la página de Cúspide.
    titulo_web = scrapy.Field()
    precio_web = scrapy.Field()
    url_imagen = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion_detallada = scrapy.Field()
    url_producto = scrapy.Field()

    # Momento en que se obtuvo el precio web.
    fecha_extraccion = scrapy.Field()