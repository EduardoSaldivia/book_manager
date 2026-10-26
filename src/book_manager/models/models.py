from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base común para todos los modelos de tablas."""
    pass


class GeneroModelo(Base):
    """Tabla de géneros literarios."""

    __tablename__ = "generos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    nombre: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    libros: Mapped[list["LibroModelo"]] = relationship(back_populates="genero")

    __table_args__ = (
        CheckConstraint("id > 0", name="ck_generos_id_positivo"),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_generos_nombre_no_vacio",
        ),
    )


class EditorialModelo(Base):
    """Tabla de editoriales."""

    __tablename__ = "editoriales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    nombre: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    libros: Mapped[list["LibroModelo"]] = relationship(back_populates="editorial")

    __table_args__ = (
        CheckConstraint("id > 0", name="ck_editoriales_id_positivo"),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_editoriales_nombre_no_vacio",
        ),
    )

class MonedaModelo(Base):
    """Tabla de monedas y sus cotizaciones fijas opcionales."""

    __tablename__ = "monedas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    codigo: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        unique=True,
    )
    nombre: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    cotizacion_ars: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True,
    )
    precios: Mapped[list["PrecioModelo"]] = relationship(back_populates="moneda")

    __table_args__ = (
        CheckConstraint("id > 0", name="ck_monedas_id_positivo"),
        CheckConstraint(
            "codigo ~ '^[A-Z]{3}$'",
            name="ck_monedas_codigo_valido",
        ),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_monedas_nombre_no_vacio",
        ),
        CheckConstraint(
            "cotizacion_ars IS NULL OR "
            "(cotizacion_ars > 0 AND "
            "cotizacion_ars < 'Infinity'::numeric)",
            name="ck_monedas_cotizacion_valida",
        ),
    )


class TipoCotizacionModelo(Base):
    """Tabla de tipos de cotización del dólar."""

    __tablename__ = "tipos_cotizacion"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    nombre: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    cotizaciones: Mapped[list["CotizacionDolarModelo"]] = relationship(
        back_populates="tipo"
    )

    __table_args__ = (
        CheckConstraint(
            "id > 0",
            name="ck_tipos_cotizacion_id_positivo",
        ),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_tipos_cotizacion_nombre_no_vacio",
        ),
    )

class LibroModelo(Base):
    """Tabla de libros, relacionados con editoriales y géneros."""

    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    isbn: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )
    titulo: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    autor: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    editorial_id: Mapped[int] = mapped_column(
        ForeignKey("editoriales.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    genero_id: Mapped[int] = mapped_column(
        ForeignKey("generos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    editorial: Mapped["EditorialModelo"] = relationship(back_populates="libros")
    genero: Mapped["GeneroModelo"] = relationship(back_populates="libros")
    precios: Mapped[list["PrecioModelo"]] = relationship(back_populates="libro")
    stock: Mapped["StockModelo | None"] = relationship(back_populates="libro")

    __table_args__ = (
        CheckConstraint(
            "id > 0",
            name="ck_libros_id_positivo",
        ),
        CheckConstraint(
            "length(trim(isbn)) > 0",
            name="ck_libros_isbn_no_vacio",
        ),
        CheckConstraint(
            "length(trim(titulo)) > 0",
            name="ck_libros_titulo_no_vacio",
        ),
        CheckConstraint(
            "length(trim(autor)) > 0",
            name="ck_libros_autor_no_vacio",
        ),
    )

class PrecioModelo(Base):
    """Tabla de precios de libros expresados en una moneda."""

    __tablename__ = "precios"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    moneda_id: Mapped[int] = mapped_column(
        ForeignKey("monedas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    importe: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    libro: Mapped["LibroModelo"] = relationship(back_populates="precios")
    moneda: Mapped["MonedaModelo"] = relationship(back_populates="precios")

    __table_args__ = (
        CheckConstraint(
            "id > 0",
            name="ck_precios_id_positivo",
        ),
        CheckConstraint(
            "importe >= 0 AND importe < 'Infinity'::numeric",
            name="ck_precios_importe_valido",
        ),
    )


class StockModelo(Base):
    """Tabla de existencias: un registro por libro."""

    __tablename__ = "stock"

    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id", ondelete="RESTRICT"),
        primary_key=True,
        autoincrement=False,
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    libro: Mapped["LibroModelo"] = relationship(back_populates="stock")

    __table_args__ = (
        CheckConstraint(
            "cantidad >= 0",
            name="ck_stock_cantidad_no_negativa",
        ),
    )

class CotizacionDolarModelo(Base):
    """Tabla de cotizaciones del dólar por tipo y fecha."""

    __tablename__ = "cotizaciones"

    tipo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_cotizacion.id", ondelete="RESTRICT"),
        primary_key=True,
        autoincrement=False,
    )
    fecha: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )
    compra: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )
    venta: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )

    tipo: Mapped["TipoCotizacionModelo"] = relationship(back_populates="cotizaciones")

    __table_args__ = (
        CheckConstraint(
            "compra > 0 AND compra < 'Infinity'::numeric",
            name="ck_cotizaciones_compra_valida",
        ),
        CheckConstraint(
            "venta > 0 AND venta < 'Infinity'::numeric",
            name="ck_cotizaciones_venta_valida",
        ),
    )

class AuditoriaModelo(Base):
    __tablename__ = "auditorias"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    accion: Mapped[str] = mapped_column(String(160), nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    detalles: Mapped[str] = mapped_column(Text, nullable=False)