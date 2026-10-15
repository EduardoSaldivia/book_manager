"""La carga inicial del Sprint 2 usa la migración explícita del ejercicio 5."""
from pathlib import Path
from book_manager.migrations.migrations import migrar_datos


class PrecargaDatos:
    def __init__(self, conexion, carpeta=None):
        self._conexion = conexion
        self._carpeta = (Path(carpeta) if carpeta is not None else
                         Path(__file__).resolve().parents[1] / "migrations" / "csv")

    def cargar(self):
        """Importa sin reemplazar registros existentes; no se ejecuta al iniciar."""
        sqls = Path(__file__).resolve().parents[1] / "migrations" / "sql"
        return migrar_datos(str(self._carpeta), str(sqls), conexion=self._conexion)
    