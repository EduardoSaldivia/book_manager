from datetime import datetime, timezone
from functools import wraps
from sqlalchemy import select
from book_manager.models.models import AuditoriaModelo


def _conexion_de(servicio):
    conexion = getattr(servicio, "_conexion", None)
    if conexion is None:
        repositorio = getattr(servicio, "_repositorio", None)
        conexion = getattr(repositorio, "_conexion", None)
    if conexion is None:
        raise AttributeError("No se encontró la conexión para auditar.")
    return conexion


def auditar_operaciones(clase):
    """Decora cada método público definido en la clase."""
    for nombre, metodo in list(vars(clase).items()):
        if nombre.startswith("_") or not callable(metodo):
            continue

        @wraps(metodo)
        def envolver(self, *args, __metodo=metodo,
                     __nombre=nombre, **kwargs):
            error = None
            try:
                return __metodo(self, *args, **kwargs)
            except Exception as exc:
                error = exc
                raise
            finally:
                detalles = f"args={args!r}; kwargs={kwargs!r}"
                detalles += "; resultado=" + (
                    "error" if error else "correcto"
                )
                if error:
                    detalles += f"; error={type(error).__name__}: {error}"
                conexion = _conexion_de(self)
                with conexion.transaccion() as sesion:
                    sesion.add(AuditoriaModelo(
                        accion=f"{type(self).__name__}.{__nombre}",
                        fecha=datetime.now(timezone.utc),
                        detalles=detalles[:4000],
                    ))
        setattr(clase, nombre, envolver)
    return clase


class ServicioAuditoria:
    def __init__(self, conexion):
        self._conexion = conexion

    def leer_historico(self, limite=100):
        limite = max(1, min(int(limite), 500))
        consulta = (
            select(AuditoriaModelo)
            .order_by(AuditoriaModelo.fecha.desc(), AuditoriaModelo.id.desc())
            .limit(limite)
        )
        with self._conexion.transaccion() as sesion:
            return list(sesion.scalars(consulta).all())