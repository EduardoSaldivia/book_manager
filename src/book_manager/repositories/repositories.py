import abc
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

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
from book_manager.models import models as m

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

class RepositorioDB:
    """Operaciones comunes. Cada operación utiliza su propia transacción."""
    modelo = None
    opciones = ()

    def __init__(self, conexion):
        self._conexion = conexion

    @contextmanager
    def _sesion(self):
        try:
            with self._conexion.transaccion() as sesion:
                yield sesion
        except IntegrityError:
            raise ValueError(
                "La operación incumple una relación, un valor único o una restricción."
            ) from None
        except SQLAlchemyError:
            raise OSError("No se pudo completar la operación en la base de datos.") from None

    def _consulta(self):
        return select(self.modelo).options(*self.opciones).order_by(
            *self.modelo.__table__.primary_key.columns
        )

    def _leer(self, clave):
        with self._sesion() as sesion:
            fila = sesion.get(self.modelo, clave, options=self.opciones)
            return None if fila is None else self._desde_modelo(fila)

    def leer_todos(self):
        with self._sesion() as sesion:
            return [self._desde_modelo(fila)
                    for fila in sesion.scalars(self._consulta()).unique()]

    def crear(self, entidad):
        with self._sesion() as sesion:
            fila = self.modelo(**self._valores(entidad))
            sesion.add(fila)
            sesion.flush()
            resultado = self._desde_modelo(fila)
        return resultado

    def actualizar(self, entidad):
        valores = self._valores(entidad)
        claves = [valores[c.name] for c in self.modelo.__table__.primary_key.columns]
        clave = claves[0] if len(claves) == 1 else tuple(claves)
        with self._sesion() as sesion:
            fila = sesion.get(self.modelo, clave)
            if fila is None:
                raise ValueError("No se encontró el registro.")
            for nombre, valor in valores.items():
                setattr(fila, nombre, valor)
            sesion.flush()
            sesion.expire(fila)
            resultado = self._desde_modelo(fila)
        return resultado

    def _eliminar(self, clave):
        with self._sesion() as sesion:
            fila = sesion.get(self.modelo, clave)
            if fila is None:
                return False
            sesion.delete(fila)
            sesion.flush()
        return True


class RepositorioEntidadDB(RepositorioDB, IRepositorio):
    def leer_por_id(self, entidad_id):
        return self._leer(entidad_id)

    def eliminar(self, entidad_id):
        return self._eliminar(entidad_id)


class RepositorioGenero(RepositorioEntidadDB):
    modelo = m.GeneroModelo

    def _valores(self, entidad):
        return {"id": entidad.id, "nombre": entidad.nombre}

    def _desde_modelo(self, fila):
        return Genero(fila.id, fila.nombre)


class RepositorioEditorial(RepositorioGenero):
    modelo = m.EditorialModelo

    def _desde_modelo(self, fila):
        return Editorial(fila.id, fila.nombre)


class RepositorioTipoCotizacion(RepositorioGenero):
    modelo = m.TipoCotizacionModelo

    def _desde_modelo(self, fila):
        return TipoCotizacion(fila.id, fila.nombre)


class RepositorioMoneda(RepositorioEntidadDB):
    modelo = m.MonedaModelo

    def _valores(self, entidad):
        return {"id": entidad.id, "codigo": entidad.codigo,
                "nombre": entidad.nombre, "cotizacion_ars": entidad.cotizacion_ars}

    def _desde_modelo(self, fila):
        return Moneda(fila.id, fila.codigo, fila.nombre, fila.cotizacion_ars)


def _libro(fila):
    return Libro(fila.id, fila.isbn, fila.titulo, fila.autor,
                 Editorial(fila.editorial.id, fila.editorial.nombre),
                 Genero(fila.genero.id, fila.genero.nombre))


class RepositorioLibro(RepositorioEntidadDB):
    modelo = m.LibroModelo
    opciones = (joinedload(m.LibroModelo.editorial), joinedload(m.LibroModelo.genero))

    def _valores(self, entidad):
        return {"id": entidad.id, "isbn": entidad.isbn, "titulo": entidad.titulo,
                "autor": entidad.autor, "editorial_id": entidad.editorial.id,
                "genero_id": entidad.genero.id}

    def _desde_modelo(self, fila):
        return _libro(fila)


class RepositorioPrecio(RepositorioEntidadDB):
    modelo = m.PrecioModelo
    opciones = (
        joinedload(m.PrecioModelo.libro).joinedload(m.LibroModelo.editorial),
        joinedload(m.PrecioModelo.libro).joinedload(m.LibroModelo.genero),
        joinedload(m.PrecioModelo.moneda),
    )

    def _valores(self, entidad):
        return {"id": entidad.id, "libro_id": entidad.libro.id,
                "moneda_id": entidad.moneda.id, "importe": entidad.importe}

    def _desde_modelo(self, fila):
        moneda = fila.moneda
        return Precio(fila.id, _libro(fila.libro),
                      Moneda(moneda.id, moneda.codigo, moneda.nombre, moneda.cotizacion_ars),
                      fila.importe)


class RepositorioStock(RepositorioDB, IRepositorioStock):
    modelo = m.StockModelo
    opciones = (
        joinedload(m.StockModelo.libro).joinedload(m.LibroModelo.editorial),
        joinedload(m.StockModelo.libro).joinedload(m.LibroModelo.genero),
    )

    def _valores(self, entidad):
        return {"libro_id": entidad.libro.id, "cantidad": entidad.cantidad}

    def _desde_modelo(self, fila):
        return Stock(_libro(fila.libro), fila.cantidad)

    def leer_por_libro(self, libro_id):
        return self._leer(libro_id)

    def eliminar(self, libro_id):
        return self._eliminar(libro_id)


class RepositorioCotizacionDolar(RepositorioDB, IRepositorioCotizacionDolar):
    modelo = m.CotizacionDolarModelo
    opciones = (joinedload(m.CotizacionDolarModelo.tipo),)

    def _valores(self, entidad):
        return {
            "tipo_id": entidad.tipo.id,
            "fecha": entidad.fecha,
            "compra": entidad.compra,
            "venta": entidad.venta,
        }

    def _desde_modelo(self, fila):
        return CotizacionDolar(
            TipoCotizacion(fila.tipo.id, fila.tipo.nombre),
            fila.fecha,
            fila.compra,
            fila.venta,
        )

    def leer_por_tipo_y_fecha(self, tipo_id, fecha):
        return self._leer((tipo_id, fecha))

    def leer_historico_por_tipo(self, tipo_id):
        with self._sesion() as sesion:
            consulta = self._consulta().where(self.modelo.tipo_id == tipo_id)
            return [self._desde_modelo(fila) for fila in sesion.scalars(consulta)]

    def eliminar(self, tipo_id, fecha):
        return self._eliminar((tipo_id, fecha))

    def guardar_lote(self, cotizaciones):
        """Inserta o actualiza todo el lote; ante un error revierte el conjunto."""
        with self._sesion() as sesion:
            for cotizacion in cotizaciones:
                sentencia = insert(self.modelo).values(**self._valores(cotizacion))
                sentencia = sentencia.on_conflict_do_update(
                    index_elements=["tipo_id", "fecha"],
                    set_={
                        "compra": sentencia.excluded.compra,
                        "venta": sentencia.excluded.venta,
                    },
                )