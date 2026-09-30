import abc
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
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

T = TypeVar("T", bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """Define las operaciones de repositorios de entidades con ID."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Guarda una entidad nueva; rechaza un ID duplicado."""
        pass

    @abc.abstractmethod
    def leer_por_id(self, entidad_id: int) -> T | None:
        """Devuelve la entidad encontrada o None si no existe."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> list[T]:
        """Devuelve todas las entidades guardadas."""
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad; rechaza un ID inexistente."""
        pass

    @abc.abstractmethod
    def eliminar(self, entidad_id: int) -> bool:
        """Devuelve True si eliminó la entidad o False si no existía."""
        pass


class RepositorioCSV(IRepositorio[T]):
    """Comparte la lectura y escritura de entidades en archivos CSV."""

    def __init__(
        self,
        ruta_archivo: str,
        columnas: list[str],
    ) -> None:
        self._ruta = Path(ruta_archivo)
        self._columnas = columnas

    @abc.abstractmethod
    def _a_fila(self, entidad: T) -> dict[str, str]:
        """Convierte una entidad en un diccionario para escribirla."""
        pass

    @abc.abstractmethod
    def _desde_fila(self, fila: dict[str, str]) -> T:
        """Construye una entidad a partir de una fila del archivo."""
        pass

    def _leer_archivo(self) -> list[T]:
        if not self._ruta.exists():
            return []

        with self._ruta.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as archivo:
            lector = csv.DictReader(archivo)
            entidades = []

            for fila in lector:
                entidad = self._desde_fila(fila)
                entidades.append(entidad)

        return entidades

    def _guardar_archivo(self, entidades: list[T]) -> None:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)

        with self._ruta.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as archivo:
            escritor = csv.DictWriter(
                archivo,
                fieldnames=self._columnas,
            )
            escritor.writeheader()

            for entidad in entidades:
                escritor.writerow(self._a_fila(entidad))
    def crear(self, entidad: T) -> T:
        """Guarda una entidad nueva y rechaza identificadores duplicados."""
        entidades = self._leer_archivo()

        for existente in entidades:
            if existente.id == entidad.id:
                raise ValueError("Ya existe una entidad con ese identificador.")

        entidades.append(entidad)
        self._guardar_archivo(entidades)
        return entidad

    def leer_por_id(self, entidad_id: int) -> T | None:
        """Construye únicamente la entidad cuya fila coincide con el ID."""
        if not self._ruta.exists():
            return None
        with self._ruta.open(mode="r", encoding="utf-8", newline="") as archivo:
            for fila in csv.DictReader(archivo):
                if int(fila["id"]) == entidad_id:
                    return self._desde_fila(fila)
        return None

    def leer_todos(self) -> list[T]:
        """Devuelve todas las entidades guardadas."""
        return self._leer_archivo()

    def actualizar(self, entidad: T) -> T:
        """Reemplaza los datos de una entidad existente."""
        entidades = self._leer_archivo()

        for indice, existente in enumerate(entidades):
            if existente.id == entidad.id:
                entidades[indice] = entidad
                self._guardar_archivo(entidades)
                return entidad

        raise ValueError("No existe una entidad con ese identificador.")

    def eliminar(self, entidad_id: int) -> bool:
        """Elimina una entidad e indica si la encontró."""
        entidades = self._leer_archivo()

        for indice, entidad in enumerate(entidades):
            if entidad.id == entidad_id:
                entidades.pop(indice)
                self._guardar_archivo(entidades)
                return True

        return False


class RepositorioGenero(RepositorioCSV[Genero]):
    """Gestiona géneros mediante el repositorio CSV compartido."""

    def __init__(self, ruta_archivo: str) -> None:
        super().__init__(ruta_archivo, ["id", "nombre"])

    def _a_fila(self, entidad: Genero) -> dict[str, str]:
        return {
            "id": str(entidad.id),
            "nombre": entidad.nombre,
        }

    def _desde_fila(self, fila: dict[str, str]) -> Genero:
        return Genero(
            entidad_id=int(fila["id"]),
            nombre=fila["nombre"],
        )


class RepositorioEditorial(RepositorioCSV[Editorial]):
    """Gestiona editoriales mediante el repositorio CSV compartido."""

    def __init__(self, ruta_archivo: str) -> None:
        super().__init__(ruta_archivo, ["id", "nombre"])

    def _a_fila(self, entidad: Editorial) -> dict[str, str]:
        return {
            "id": str(entidad.id),
            "nombre": entidad.nombre,
        }

    def _desde_fila(self, fila: dict[str, str]) -> Editorial:
        return Editorial(
            entidad_id=int(fila["id"]),
            nombre=fila["nombre"],
        )


class RepositorioMoneda(RepositorioCSV[Moneda]):
    """Guarda monedas y sus cotizaciones fijas opcionales."""

    def __init__(self, ruta_archivo: str) -> None:
        super().__init__(
            ruta_archivo,
            ["id", "codigo", "nombre", "cotizacion_ars"],
        )

    def _a_fila(self, entidad: Moneda) -> dict[str, str]:
        return {
            "id": str(entidad.id),
            "codigo": entidad.codigo,
            "nombre": entidad.nombre,
            "cotizacion_ars": (
                str(entidad.cotizacion_ars)
                if entidad.cotizacion_ars is not None
                else ""
            ),
        }

    def _desde_fila(self, fila: dict[str, str]) -> Moneda:
        texto_cotizacion = (fila.get("cotizacion_ars") or "").strip()

        cotizacion = (
            Decimal(texto_cotizacion)
            if texto_cotizacion
            else None
        )

        return Moneda(
            entidad_id=int(fila["id"]),
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            cotizacion_ars=cotizacion,
        )


class RepositorioTipoCotizacion(RepositorioCSV[TipoCotizacion]):
    """Gestiona los tipos de cotización mediante archivos CSV."""

    def __init__(self, ruta_archivo: str) -> None:
        super().__init__(ruta_archivo, ["id", "nombre"])

    def _a_fila(self, entidad: TipoCotizacion) -> dict[str, str]:
        return {
            "id": str(entidad.id),
            "nombre": entidad.nombre,
        }

    def _desde_fila(self, fila: dict[str, str]) -> TipoCotizacion:
        return TipoCotizacion(
            entidad_id=int(fila["id"]),
            nombre=fila["nombre"],
        )

class RepositorioLibro(RepositorioCSV[Libro]):
    """Gestiona libros y reconstruye sus relaciones desde archivos CSV."""

    def __init__(
        self,
        ruta_archivo: str,
        repo_editoriales: IRepositorio[Editorial],
        repo_generos: IRepositorio[Genero],
    ) -> None:
        super().__init__(
            ruta_archivo,
            ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"],
        )
        self._repo_editoriales = repo_editoriales
        self._repo_generos = repo_generos

    def _a_fila(self, entidad: Libro) -> dict[str, str]:
        return {
            "id": str(entidad.id),
            "isbn": entidad.isbn,
            "titulo": entidad.titulo,
            "autor": entidad.autor,
            "editorial_id": str(entidad.editorial.id),
            "genero_id": str(entidad.genero.id),
        }

    def _desde_fila(self, fila: dict[str, str]) -> Libro:
        editorial_id = int(fila["editorial_id"])
        genero_id = int(fila["genero_id"])

        editorial = self._repo_editoriales.leer_por_id(editorial_id)
        genero = self._repo_generos.leer_por_id(genero_id)

        if editorial is None:
            raise ValueError(
                f"No existe la editorial {editorial_id} del libro."
            )

        if genero is None:
            raise ValueError(
                f"No existe el género {genero_id} del libro."
            )

        return Libro(
            entidad_id=int(fila["id"]),
            isbn=fila["isbn"],
            titulo=fila["titulo"],
            autor=fila["autor"],
            editorial=editorial,
            genero=genero,
        )


class RepositorioPrecio(RepositorioCSV[Precio]):
    """Gestiona precios relacionados con libros y monedas."""

    def __init__(
        self,
        ruta_archivo: str,
        repo_libros: IRepositorio[Libro],
        repo_monedas: IRepositorio[Moneda],
    ) -> None:
        super().__init__(
            ruta_archivo,
            ["id", "libro_id", "moneda_id", "importe"],
        )
        self._repo_libros = repo_libros
        self._repo_monedas = repo_monedas

    def _a_fila(self, entidad: Precio) -> dict[str, str]:
        return {
            "id": str(entidad.id),
            "libro_id": str(entidad.libro.id),
            "moneda_id": str(entidad.moneda.id),
            "importe": str(entidad.importe),
        }

    def _desde_fila(self, fila: dict[str, str]) -> Precio:
        libro_id = int(fila["libro_id"])
        moneda_id = int(fila["moneda_id"])

        libro = self._repo_libros.leer_por_id(libro_id)
        moneda = self._repo_monedas.leer_por_id(moneda_id)

        if libro is None:
            raise ValueError(
                f"No existe el libro {libro_id} del precio."
            )

        if moneda is None:
            raise ValueError(
                f"No existe la moneda {moneda_id} del precio."
            )

        return Precio(
            entidad_id=int(fila["id"]),
            libro=libro,
            moneda=moneda,
            importe=Decimal(fila["importe"]),
        )


class IRepositorioStock(abc.ABC):
    """Define las operaciones de stock identificado por libro."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Guarda el stock y rechaza un libro que ya tenga registro."""
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Stock | None:
        """Devuelve el stock del libro o None si no existe."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> list[Stock]:
        """Devuelve todos los registros de stock."""
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza el stock de un libro que ya tenga registro."""
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Devuelve True si eliminó el registro o False si no existía."""
        pass


class RepositorioStock(IRepositorioStock):
    """Gestiona el stock de los libros en un archivo CSV."""

    def __init__(
        self,
        ruta_archivo: str,
        repo_libros: IRepositorio[Libro],
    ) -> None:
        self._ruta = Path(ruta_archivo)
        self._repo_libros = repo_libros

    def _leer_archivo(self) -> list[Stock]:
        if not self._ruta.exists():
            return []

        with self._ruta.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as archivo:
            lector = csv.DictReader(archivo)
            registros = []

            for fila in lector:
                libro_id = int(fila["libro_id"])
                libro = self._repo_libros.leer_por_id(libro_id)

                if libro is None:
                    raise ValueError(
                        f"No existe el libro {libro_id} del stock."
                    )

                stock = Stock(
                    libro=libro,
                    cantidad=int(fila["cantidad"]),
                )
                registros.append(stock)

        return registros

    def _guardar_archivo(self, registros: list[Stock]) -> None:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)

        with self._ruta.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as archivo:
            escritor = csv.DictWriter(
                archivo,
                fieldnames=["libro_id", "cantidad"],
            )
            escritor.writeheader()

            for stock in registros:
                escritor.writerow({
                    "libro_id": stock.libro.id,
                    "cantidad": stock.cantidad,
                })

    def crear(self, stock: Stock) -> Stock:
        """Crea un registro de stock sin repetir el libro."""
        registros = self._leer_archivo()

        for existente in registros:
            if existente.libro.id == stock.libro.id:
                raise ValueError("Ya existe un registro de stock para el libro.")

        if self._repo_libros.leer_por_id(stock.libro.id) is None:
            raise ValueError("El libro debe estar guardado antes de crear stock.")

        registros.append(stock)
        self._guardar_archivo(registros)
        return stock

    def leer_por_libro(self, libro_id: int) -> Stock | None:
        """Lee únicamente el stock y el libro solicitados."""
        if not self._ruta.exists():
            return None
        with self._ruta.open(mode="r", encoding="utf-8", newline="") as archivo:
            for fila in csv.DictReader(archivo):
                if int(fila["libro_id"]) == libro_id:
                    libro = self._repo_libros.leer_por_id(libro_id)
                    if libro is None:
                        raise ValueError(f"No existe el libro {libro_id} del stock.")
                    return Stock(libro=libro, cantidad=int(fila["cantidad"]))
        return None

    def leer_todos(self) -> list[Stock]:
        """Devuelve todos los registros de stock."""
        return self._leer_archivo()

    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza el registro de stock de un libro existente."""
        registros = self._leer_archivo()

        for indice, existente in enumerate(registros):
            if existente.libro.id == stock.libro.id:
                registros[indice] = stock
                self._guardar_archivo(registros)
                return stock

        raise ValueError("No existe un registro de stock para el libro.")

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el registro de stock sin eliminar el libro."""
        registros = self._leer_archivo()

        for indice, stock in enumerate(registros):
            if stock.libro.id == libro_id:
                registros.pop(indice)
                self._guardar_archivo(registros)
                return True

        return False


class IRepositorioCotizacionDolar(abc.ABC):
    """Define operaciones de cotizaciones identificadas por tipo y fecha."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización y rechaza una combinación duplicada."""
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> CotizacionDolar | None:
        """Busca una cotización por tipo y fecha."""
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(
        self,
        tipo_id: int,
    ) -> list[CotizacionDolar]:
        """Devuelve las cotizaciones del tipo ordenadas por fecha."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> list[CotizacionDolar]:
        """Devuelve todas las cotizaciones guardadas."""
        pass

    @abc.abstractmethod
    def actualizar(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        """Actualiza una cotización existente."""
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización e indica si la encontró."""
        pass


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Gestiona cotizaciones históricas del dólar en un archivo CSV."""

    def __init__(
        self,
        ruta_archivo: str,
        repo_tipos: IRepositorio[TipoCotizacion],
    ) -> None:
        self._ruta = Path(ruta_archivo)
        self._repo_tipos = repo_tipos

    def _leer_archivo(self) -> list[CotizacionDolar]:
        if not self._ruta.exists():
            return []

        with self._ruta.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as archivo:
            lector = csv.DictReader(archivo)
            cotizaciones = []

            for fila in lector:
                tipo_id = int(fila["tipo_id"])
                tipo = self._repo_tipos.leer_por_id(tipo_id)

                if tipo is None:
                    raise ValueError(
                        f"No existe el tipo de cotización {tipo_id}."
                    )

                cotizacion = CotizacionDolar(
                    tipo=tipo,
                    fecha=date.fromisoformat(fila["fecha"]),
                    valor=Decimal(fila["valor"]),
                )
                cotizaciones.append(cotizacion)

        return cotizaciones

    def _guardar_archivo(
        self,
        cotizaciones: list[CotizacionDolar],
    ) -> None:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)

        with self._ruta.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as archivo:
            escritor = csv.DictWriter(
                archivo,
                fieldnames=["tipo_id", "fecha", "valor"],
            )
            escritor.writeheader()

            for cotizacion in cotizaciones:
                escritor.writerow({
                    "tipo_id": cotizacion.tipo.id,
                    "fecha": cotizacion.fecha.isoformat(),
                    "valor": str(cotizacion.valor),
                })

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización sin repetir la combinación tipo y fecha."""
        cotizaciones = self._leer_archivo()

        for existente in cotizaciones:
            if (
                existente.tipo.id == cotizacion.tipo.id
                and existente.fecha == cotizacion.fecha
            ):
                raise ValueError(
                    "Ya existe una cotización para ese tipo y fecha."
                )

        if self._repo_tipos.leer_por_id(cotizacion.tipo.id) is None:
            raise ValueError(
                "El tipo de cotización debe estar guardado previamente."
            )

        cotizaciones.append(cotizacion)
        self._guardar_archivo(cotizaciones)
        return cotizacion

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> CotizacionDolar | None:
        """Busca una cotización por su tipo y fecha."""
        cotizaciones = self._leer_archivo()

        for cotizacion in cotizaciones:
            if cotizacion.tipo.id == tipo_id and cotizacion.fecha == fecha:
                return cotizacion

        return None

    def leer_historico_por_tipo(
        self,
        tipo_id: int,
    ) -> list[CotizacionDolar]:
        """Devuelve el histórico del tipo, de la fecha más antigua a la nueva."""
        cotizaciones = self._leer_archivo()
        historico = []

        for cotizacion in cotizaciones:
            if cotizacion.tipo.id == tipo_id:
                historico.append(cotizacion)

        return sorted(historico, key=lambda cotizacion: cotizacion.fecha)

    def leer_todos(self) -> list[CotizacionDolar]:
        """Devuelve todas las cotizaciones guardadas."""
        return self._leer_archivo()

    def actualizar(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        """Actualiza el valor de una cotización existente."""
        cotizaciones = self._leer_archivo()

        for indice, existente in enumerate(cotizaciones):
            if (
                existente.tipo.id == cotizacion.tipo.id
                and existente.fecha == cotizacion.fecha
            ):
                cotizaciones[indice] = cotizacion
                self._guardar_archivo(cotizaciones)
                return cotizacion

        raise ValueError("No existe una cotización para ese tipo y fecha.")

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización identificada por tipo y fecha."""
        cotizaciones = self._leer_archivo()

        for indice, cotizacion in enumerate(cotizaciones):
            if cotizacion.tipo.id == tipo_id and cotizacion.fecha == fecha:
                cotizaciones.pop(indice)
                self._guardar_archivo(cotizaciones)
                return True

        return False