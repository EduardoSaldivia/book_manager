import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


CARPETA_JSON = Path(__file__).resolve().parents[1] / "migrations" / "json"


def leer_documento(ruta: Path) -> dict[str, Any]:
    """Lee un objeto JSON local y conserva la precisión de los decimales."""
    try:
        with ruta.open(encoding="utf-8-sig") as archivo:
            documento = json.load(archivo, parse_float=Decimal)
    except FileNotFoundError as error:
        raise ValueError(f"No se encontró el archivo JSON: {ruta}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON incorrecto en {ruta.name}, línea {error.lineno}, "
            f"columna {error.colno}. Revisá comas y comillas."
        ) from error
    except (OSError, UnicodeError) as error:
        raise ValueError(
            f"No se pudo leer {ruta.name}. Revisá el acceso y la codificación UTF-8."
        ) from error

    if not isinstance(documento, dict):
        raise ValueError(f"{ruta.name} debe contener un objeto JSON.")
    return documento


def leer_texto(valor: object, campo: str) -> str:
    """Valida un texto obligatorio y elimina espacios exteriores."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo '{campo}' del JSON debe tener texto.")
    return valor.strip()


def leer_fecha(valor: object, campo: str) -> date:
    """Valida una fecha de calendario en formato AAAA-MM-DD."""
    texto = leer_texto(valor, campo)
    try:
        fecha = date.fromisoformat(texto)
    except ValueError as error:
        raise ValueError(
            f"El campo '{campo}' debe ser una fecha válida AAAA-MM-DD."
        ) from error
    if fecha.isoformat() != texto:
        raise ValueError(f"El campo '{campo}' debe usar AAAA-MM-DD.")
    return fecha


def leer_importe(valor: object, campo: str) -> Decimal:
    """Acepta importes numéricos o escritos como texto, finitos y positivos."""
    if isinstance(valor, bool) or not isinstance(valor, (str, int, Decimal)):
        raise ValueError(f"El campo '{campo}' debe ser un importe positivo.")
    try:
        importe = Decimal(valor)
    except InvalidOperation as error:
        raise ValueError(f"El campo '{campo}' no es un importe válido.") from error
    if not importe.is_finite() or importe <= 0:
        raise ValueError(f"El campo '{campo}' debe ser finito y mayor que cero.")
    return importe


def leer_registros(
    documento: dict[str, Any], campo: str
) -> list[dict[str, Any]]:
    """Comprueba que una colección del JSON contenga objetos."""
    registros = documento.get(campo)
    if not isinstance(registros, list) or any(
        not isinstance(registro, dict) for registro in registros
    ):
        raise ValueError(f"El campo '{campo}' debe ser una lista de objetos.")
    return registros
