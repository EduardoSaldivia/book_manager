from decimal import Decimal #UTILIZADA EN CLASE PRECIO
from datetime import date   #UTILIZADA EN CLASE COTIZACIONDOLAR

class EntidadBase:
    """Representa una entidad con un identificador positivo."""

    def __init__(self, entidad_id: int) -> None:
        if type(entidad_id) is not int:
            raise ValueError("El identificador debe ser un número entero.")

        if entidad_id <= 0:
            raise ValueError("El identificador debe ser mayor que cero.")

        self._id = entidad_id

    @property
    def id(self) -> int:
        return self._id


class Genero(EntidadBase):
    """Representa un género literario."""

    def __init__(self, entidad_id: int, nombre: str) -> None:
        super().__init__(entidad_id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        nuevo_nombre = nuevo_nombre.strip()

        if not nuevo_nombre:
            raise ValueError("El nombre del género no puede estar vacío.")

        self._nombre = nuevo_nombre 


class Editorial(EntidadBase):
    """Representa una editorial de libros."""

    def __init__(self, entidad_id: int, nombre: str) -> None:
        super().__init__(entidad_id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        nuevo_nombre = nuevo_nombre.strip()

        if not nuevo_nombre:
            raise ValueError("El nombre de la editorial no puede estar vacío.")

        self._nombre = nuevo_nombre


class Moneda(EntidadBase):
    """Representa una moneda y su cotización fija opcional en pesos."""

    def __init__(
        self,
        entidad_id: int,
        codigo: str,
        nombre: str,
        cotizacion_ars: Decimal | None = None,
    ) -> None:
        super().__init__(entidad_id)
        self.codigo = codigo
        self.nombre = nombre
        self.cotizacion_ars = cotizacion_ars

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, nuevo_codigo: str) -> None:
        nuevo_codigo = nuevo_codigo.strip().upper()

        if len(nuevo_codigo) != 3 or not nuevo_codigo.isalpha():
            raise ValueError(
                "El código debe contener exactamente tres letras."
            )

        self._codigo = nuevo_codigo

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        nuevo_nombre = nuevo_nombre.strip()

        if not nuevo_nombre:
            raise ValueError("El nombre de la moneda no puede estar vacío.")

        self._nombre = nuevo_nombre

    @property
    def cotizacion_ars(self) -> Decimal | None:
        """Devuelve los pesos por unidad, o None si falta configurarlos."""
        return self._cotizacion_ars

    @cotizacion_ars.setter
    def cotizacion_ars(self, nuevo_valor: Decimal | None) -> None:
        if nuevo_valor is None:
            self._cotizacion_ars = None
            return

        if not isinstance(nuevo_valor, Decimal):
            raise ValueError("La cotización debe ser un Decimal.")

        if not nuevo_valor.is_finite() or nuevo_valor <= 0:
            raise ValueError(
                "La cotización debe ser un número finito mayor que cero."
            )

        self._cotizacion_ars = nuevo_valor


class TipoCotizacion(EntidadBase):
    """Representa un tipo de cotización del dólar."""

    def __init__(self, entidad_id: int, nombre: str) -> None:
        super().__init__(entidad_id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        nuevo_nombre = nuevo_nombre.strip()

        if not nuevo_nombre:
            raise ValueError(
                "El nombre del tipo de cotización no puede estar vacío."
            )

        self._nombre = nuevo_nombre


class Libro(EntidadBase):
    """Representa un libro relacionado con una editorial y un género."""

    def __init__(
        self,
        entidad_id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial: Editorial,
        genero: Genero,
    ) -> None:
        super().__init__(entidad_id)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.genero = genero

    @property
    def editorial(self) -> Editorial:
        return self._editorial

    @editorial.setter
    def editorial(self, nueva_editorial: Editorial) -> None:
        if not isinstance(nueva_editorial, Editorial):
            raise ValueError("La editorial debe ser un objeto Editorial.")

        self._editorial = nueva_editorial

    @property
    def genero(self) -> Genero:
        return self._genero

    @genero.setter
    def genero(self, nuevo_genero: Genero) -> None:
        if not isinstance(nuevo_genero, Genero):
            raise ValueError("El género debe ser un objeto Genero.")

        self._genero = nuevo_genero

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, nuevo_isbn: str) -> None:
        nuevo_isbn = nuevo_isbn.strip()

        if not nuevo_isbn:
            raise ValueError("El ISBN no puede estar vacío.")

        self._isbn = nuevo_isbn

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, nuevo_titulo: str) -> None:
        nuevo_titulo = nuevo_titulo.strip()

        if not nuevo_titulo:
            raise ValueError("El título no puede estar vacío.")

        self._titulo = nuevo_titulo

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, nuevo_autor: str) -> None:
        nuevo_autor = nuevo_autor.strip()

        if not nuevo_autor:
            raise ValueError("El autor no puede estar vacío.")

        self._autor = nuevo_autor


class Stock:
    """Representa la cantidad disponible de un libro."""

    def __init__(self, libro: Libro, cantidad: int) -> None:
        if not isinstance(libro, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")

        self._libro = libro
        self.cantidad = cantidad

    @property
    def libro(self) -> Libro:
        return self._libro

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, nueva_cantidad: int) -> None:
        if type(nueva_cantidad) is not int:
            raise ValueError("La cantidad debe ser un número entero.")

        if nueva_cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")

        self._cantidad = nueva_cantidad


class Precio(EntidadBase):
    """Representa el importe de un libro en una moneda determinada."""

    def __init__(
        self,
        entidad_id: int,
        libro: Libro,
        moneda: Moneda,
        importe: Decimal,
    ) -> None:
        super().__init__(entidad_id)

        if not isinstance(libro, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")

        self._libro = libro
        self.moneda = moneda
        self.importe = importe

    @property
    def libro(self) -> Libro:
        return self._libro

    @property
    def moneda(self) -> Moneda:
        return self._moneda

    @moneda.setter
    def moneda(self, nueva_moneda: Moneda) -> None:
        if not isinstance(nueva_moneda, Moneda):
            raise ValueError("La moneda debe ser un objeto Moneda.")

        self._moneda = nueva_moneda

    @property
    def importe(self) -> Decimal:
        return self._importe

    @importe.setter
    def importe(self, nuevo_importe: Decimal) -> None:
        if not isinstance(nuevo_importe, Decimal):
            raise ValueError("El importe debe ser un objeto Decimal.")

        if not nuevo_importe.is_finite():
            raise ValueError("El importe debe ser un número finito.")

        if nuevo_importe < 0:
            raise ValueError("El importe no puede ser negativo.")

        self._importe = nuevo_importe


class CotizacionDolar:
    """Registra el valor en pesos de un dólar por tipo y fecha."""

    def __init__(
        self,
        tipo: TipoCotizacion,
        fecha: date,
        valor: Decimal,
    ) -> None:
        if not isinstance(tipo, TipoCotizacion):
            raise ValueError("El tipo debe ser un objeto TipoCotizacion.")

        if type(fecha) is not date:
            raise ValueError("La fecha debe ser un objeto date.")

        self._tipo = tipo
        self._fecha = fecha
        self.valor = valor

    @property
    def tipo(self) -> TipoCotizacion:
        return self._tipo

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def valor(self) -> Decimal:
        return self._valor

    @valor.setter
    def valor(self, nuevo_valor: Decimal) -> None:
        if not isinstance(nuevo_valor, Decimal):
            raise ValueError("El valor debe ser un objeto Decimal.")

        if not nuevo_valor.is_finite():
            raise ValueError("El valor debe ser un número finito.")

        if nuevo_valor <= 0:
            raise ValueError("El valor debe ser mayor que cero.")

        self._valor = nuevo_valor