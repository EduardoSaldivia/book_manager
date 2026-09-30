from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Generic, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    IRepositorio,
    IRepositorioCotizacionDolar,
    IRepositorioStock,
)


T = TypeVar("T", bound=EntidadBase)


class ServicioBase(Generic[T]):
    """Coordina el CRUD y permite agregar reglas específicas."""

    def __init__(self, repositorio: IRepositorio[T]) -> None:
        self._repositorio = repositorio

    def _validar_guardado(self, entidad: T) -> None:
        """Permite agregar validaciones antes de crear o actualizar."""
        pass

    def _validar_eliminacion(self, entidad_id: int) -> None:
        """Permite agregar validaciones antes de eliminar."""
        pass

    def crear(self, entidad: T) -> T:
        """Valida las reglas y guarda una entidad nueva."""
        self._validar_guardado(entidad)
        return self._repositorio.crear(entidad)

    def leer_por_id(self, entidad_id: int) -> T | None:
        """Consulta una entidad por su identificador."""
        return self._repositorio.leer_por_id(entidad_id)

    def leer_todos(self) -> list[T]:
        """Consulta todas las entidades."""
        return self._repositorio.leer_todos()

    def actualizar(self, entidad: T) -> T:
        """Valida las reglas y actualiza una entidad existente."""
        self._validar_guardado(entidad)
        return self._repositorio.actualizar(entidad)

    def eliminar(self, entidad_id: int) -> bool:
        """Elimina una entidad si existe y las reglas lo permiten."""
        if self._repositorio.leer_por_id(entidad_id) is None:
            return False

        self._validar_eliminacion(entidad_id)
        return self._repositorio.eliminar(entidad_id)


class ServicioGenero(ServicioBase[Genero]):
    """Gestiona géneros y protege sus relaciones con libros."""

    def __init__(
        self,
        repositorio: IRepositorio[Genero],
        repo_libros: IRepositorio[Libro],
    ) -> None:
        super().__init__(repositorio)
        self._repo_libros = repo_libros

    def _validar_eliminacion(self, entidad_id: int) -> None:
        """Impide eliminar un género utilizado por algún libro."""
        for libro in self._repo_libros.leer_todos():
            if libro.genero.id == entidad_id:
                raise ValueError(
                    "No se puede eliminar un género utilizado por libros."
                )


class ServicioEditorial(ServicioBase[Editorial]):
    """Gestiona editoriales y protege sus relaciones con libros."""

    def __init__(
        self,
        repositorio: IRepositorio[Editorial],
        repo_libros: IRepositorio[Libro],
    ) -> None:
        super().__init__(repositorio)
        self._repo_libros = repo_libros

    def _validar_eliminacion(self, entidad_id: int) -> None:
        """Impide eliminar una editorial utilizada por algún libro."""
        for libro in self._repo_libros.leer_todos():
            if libro.editorial.id == entidad_id:
                raise ValueError(
                    "No se puede eliminar una editorial utilizada por libros."
                )


class ServicioMoneda(ServicioBase[Moneda]):
    """Gestiona monedas y protege sus relaciones con precios."""

    def __init__(
        self,
        repositorio: IRepositorio[Moneda],
        repo_precios: IRepositorio[Precio],
    ) -> None:
        super().__init__(repositorio)
        self._repo_precios = repo_precios

    def _validar_eliminacion(self, entidad_id: int) -> None:
        """Impide eliminar una moneda utilizada en precios."""
        for precio in self._repo_precios.leer_todos():
            if precio.moneda.id == entidad_id:
                raise ValueError(
                    "No se puede eliminar una moneda utilizada en precios."
                )


class ServicioTipoCotizacion(ServicioBase[TipoCotizacion]):
    """Gestiona tipos y protege sus cotizaciones históricas."""

    def __init__(
        self,
        repositorio: IRepositorio[TipoCotizacion],
        repo_cotizaciones: IRepositorioCotizacionDolar,
    ) -> None:
        super().__init__(repositorio)
        self._repo_cotizaciones = repo_cotizaciones

    def _validar_eliminacion(self, entidad_id: int) -> None:
        """Impide eliminar un tipo que tenga cotizaciones."""
        historico = self._repo_cotizaciones.leer_historico_por_tipo(
            entidad_id
        )

        if historico:
            raise ValueError(
                "No se puede eliminar un tipo que tiene cotizaciones."
            )


class ServicioLibro(ServicioBase[Libro]):
    """Gestiona libros y comprueba sus relaciones."""

    def __init__(
        self,
        repositorio: IRepositorio[Libro],
        repo_editoriales: IRepositorio[Editorial],
        repo_generos: IRepositorio[Genero],
        repo_precios: IRepositorio[Precio],
        repo_stock: IRepositorioStock,
    ) -> None:
        super().__init__(repositorio)
        self._repo_editoriales = repo_editoriales
        self._repo_generos = repo_generos
        self._repo_precios = repo_precios
        self._repo_stock = repo_stock

    def _validar_guardado(self, entidad: Libro) -> None:
        """Comprueba que la editorial y el género estén guardados."""
        editorial = self._repo_editoriales.leer_por_id(
            entidad.editorial.id
        )
        genero = self._repo_generos.leer_por_id(entidad.genero.id)

        if editorial is None:
            raise ValueError("La editorial del libro no está registrada.")

        if genero is None:
            raise ValueError("El género del libro no está registrado.")

    def _validar_eliminacion(self, entidad_id: int) -> None:
        """Impide eliminar un libro con precios o registro de stock."""
        for precio in self._repo_precios.leer_todos():
            if precio.libro.id == entidad_id:
                raise ValueError(
                    "Primero deben eliminarse los precios del libro."
                )

        if self._repo_stock.leer_por_libro(entidad_id) is not None:
            raise ValueError(
                "Primero debe eliminarse el registro de stock del libro."
            )


class ServicioPrecio(ServicioBase[Precio]):
    """Gestiona precios y conversiones entre pesos y dólares."""

    def __init__(
        self,
        repositorio: IRepositorio[Precio],
        repo_libros: IRepositorio[Libro],
        repo_monedas: IRepositorio[Moneda],
        repo_cotizaciones: IRepositorioCotizacionDolar,
    ) -> None:
        super().__init__(repositorio)
        self._repo_libros = repo_libros
        self._repo_monedas = repo_monedas
        self._repo_cotizaciones = repo_cotizaciones

    def _validar_guardado(self, entidad: Precio) -> None:
        """Comprueba que el libro y la moneda estén guardados."""
        libro = self._repo_libros.leer_por_id(entidad.libro.id)
        moneda = self._repo_monedas.leer_por_id(entidad.moneda.id)

        if libro is None:
            raise ValueError("El libro del precio no está registrado.")

        if moneda is None:
            raise ValueError("La moneda del precio no está registrada.")

    def _pesos_por_unidad(
        self,
        moneda: Moneda,
        tipo_id: int | None,
        fecha: date | None,
    ) -> Decimal:
        """Resuelve la tasa fija o la cotización histórica del dólar."""
        if moneda.codigo == "ARS":
            return Decimal("1")
        if moneda.codigo == "USD":
            if tipo_id is None or fecha is None:
                raise ValueError("Para USD indicá el tipo y la fecha de cotización.")
            cotizacion = self._repo_cotizaciones.leer_por_tipo_y_fecha(tipo_id, fecha)
            if cotizacion is None:
                raise ValueError("No hay cotización del dólar para ese tipo y fecha.")
            return cotizacion.valor
        if moneda.cotizacion_ars is None:
            raise ValueError(
                f"Falta la cotización fija de {moneda.codigo} en monedas.csv."
            )
        return moneda.cotizacion_ars

    def convertir_precio(
        self,
        precio_id: int,
        moneda_destino_id: int,
        tipo_id: int | None = None,
        fecha: date | None = None,
    ) -> Decimal:
        """Convierte pasando por ARS, sin cambiar el importe guardado."""
        precio = self._repositorio.leer_por_id(precio_id)
        destino = self._repo_monedas.leer_por_id(moneda_destino_id)
        if precio is None:
            raise ValueError("No existe el precio solicitado.")
        if destino is None:
            raise ValueError("No existe la moneda de destino.")
        origen = self._repo_monedas.leer_por_id(precio.moneda.id)
        if origen is None:
            raise ValueError("No existe la moneda de origen.")
        if origen.codigo == destino.codigo:
            resultado = precio.importe
        else:
            tasa_origen = self._pesos_por_unidad(origen, tipo_id, fecha)
            tasa_destino = self._pesos_por_unidad(destino, tipo_id, fecha)
            resultado = precio.importe * tasa_origen / tasa_destino
        return resultado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ServicioStock:
    """Gestiona existencias y comprueba la existencia del libro."""

    def __init__(
        self,
        repositorio: IRepositorioStock,
        repo_libros: IRepositorio[Libro],
    ) -> None:
        self._repositorio = repositorio
        self._repo_libros = repo_libros

    def _validar_guardado(self, stock: Stock) -> None:
        """Comprueba que el libro esté registrado."""
        if self._repo_libros.leer_por_id(stock.libro.id) is None:
            raise ValueError("El libro del stock no está registrado.")

    def crear(self, stock: Stock) -> Stock:
        """Valida y crea un registro de stock."""
        self._validar_guardado(stock)
        return self._repositorio.crear(stock)

    def leer_por_libro(self, libro_id: int) -> Stock | None:
        """Consulta el stock de un libro."""
        return self._repositorio.leer_por_libro(libro_id)

    def leer_todos(self) -> list[Stock]:
        """Consulta todos los registros de stock."""
        return self._repositorio.leer_todos()

    def actualizar(self, stock: Stock) -> Stock:
        """Valida y actualiza un registro de stock."""
        self._validar_guardado(stock)
        return self._repositorio.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el registro de stock de un libro."""
        return self._repositorio.eliminar(libro_id)


class ServicioCotizacionDolar:
    """Gestiona cotizaciones y comprueba sus tipos asociados."""

    def __init__(
        self,
        repositorio: IRepositorioCotizacionDolar,
        repo_tipos: IRepositorio[TipoCotizacion],
    ) -> None:
        self._repositorio = repositorio
        self._repo_tipos = repo_tipos

    def _validar_guardado(self, cotizacion: CotizacionDolar) -> None:
        """Comprueba que el tipo de cotización esté registrado."""
        if self._repo_tipos.leer_por_id(cotizacion.tipo.id) is None:
            raise ValueError("El tipo de cotización no está registrado.")

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Valida y crea una cotización."""
        self._validar_guardado(cotizacion)
        return self._repositorio.crear(cotizacion)

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> CotizacionDolar | None:
        """Consulta una cotización por tipo y fecha."""
        return self._repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)

    def leer_historico_por_tipo(
        self,
        tipo_id: int,
    ) -> list[CotizacionDolar]:
        """Consulta el histórico de un tipo ordenado por fecha."""
        return self._repositorio.leer_historico_por_tipo(tipo_id)

    def leer_todos(self) -> list[CotizacionDolar]:
        """Consulta todas las cotizaciones."""
        return self._repositorio.leer_todos()

    def actualizar(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        """Valida y actualiza una cotización."""
        self._validar_guardado(cotizacion)
        return self._repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha."""
        return self._repositorio.eliminar(tipo_id, fecha)