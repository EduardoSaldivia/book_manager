import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy.orm import Session


class ConexionDB:
    """Administra la conexión con PostgreSQL en Supabase."""

    def __init__(self) -> None:
        # Busca el .env en la raíz del proyecto.
        raiz_proyecto = Path(__file__).resolve().parents[3]
        load_dotenv(raiz_proyecto / ".env")

        # Comprueba que estén los datos necesarios.
        obligatorias = (
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",
        )

        faltantes = [
            nombre
            for nombre in obligatorias
            if not os.getenv(nombre)
        ]

        if faltantes:
            raise ValueError(
                "Faltan variables de configuración: "
                + ", ".join(faltantes)
            )

        # Construye la dirección sin concatenar la contraseña.
        url = URL.create(
            drivername="postgresql+psycopg",
            username=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            database=os.environ["DB_NAME"],
        )

        # Prepara el motor que usará SQLAlchemy.
        self.engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 10,
            },
        )

    def probar_conexion(self) -> bool:
        """Ejecuta una consulta sencilla para verificar la conexión."""
        with self.engine.connect() as conexion:
            resultado = conexion.execute(text("SELECT 1"))
            return resultado.scalar_one() == 1

    def cerrar(self) -> None:
        """Libera las conexiones disponibles del motor."""
        self.engine.dispose()


    @contextmanager
    def transaccion(self) -> Iterator[Session]:
        """Confirma los cambios si todo sale bien o los revierte si falla."""
        with Session(self.engine) as sesion:
            with sesion.begin():
                yield sesion

    def crear_tablas(self) -> None:
        """Crea en la base las tablas definidas por los modelos."""
        from book_manager.models.models import Base

        with self.engine.begin() as conexion:
            Base.metadata.create_all(conexion)
