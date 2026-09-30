import csv
import os
import re
import shutil
import sys
import textwrap
from dataclasses import dataclass
from datetime import date, timedelta, timezone
from book_manager.services.dolar_api import ClienteDolarAPI
from decimal import Decimal, InvalidOperation
from typing import Any, Callable
from book_manager.services.cuspide_api import ClienteCuspideAPI

from book_manager.entities import entities as entidades
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)


# ======================================================================
# Apariencia de la consola
# ----------------------------------------------------------------------
# Este bloque solo decide cómo se ve la información en pantalla
# (colores, recuadros, tablas y barras). No toca datos ni servicios.
# Los colores se apagan solos si la salida no es una terminal o si
# existe la variable de entorno NO_COLOR.
# ======================================================================

if os.name == "nt":
    # Habilita los códigos de color en la consola de Windows 10 o superior.
    try:
        import ctypes

        _kernel32 = ctypes.windll.kernel32
        _salida = _kernel32.GetStdHandle(-11)
        _modo = ctypes.c_uint32()

        if _kernel32.GetConsoleMode(_salida, ctypes.byref(_modo)):
            _kernel32.SetConsoleMode(_salida, _modo.value | 0x0004)
    except Exception:
        pass

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_NUMERO = re.compile(r"^-?\d{1,9}(?:[.,]\d+)?$")

_CODIGOS = {
    "negrita": "1",
    "rojo": "31",
    "verde": "32",
    "amarillo": "33",
    "azul": "34",
    "magenta": "35",
    "cian": "36",
    "gris": "90",
}

_SIMBOLOS_UNICODE = {
    "sup_izq": "┌",
    "sup_der": "┐",
    "inf_izq": "└",
    "inf_der": "┘",
    "horizontal": "─",
    "vertical": "│",
    "cruce": "┼",
    "doble_sup_izq": "╔",
    "doble_sup_der": "╗",
    "doble_inf_izq": "╚",
    "doble_inf_der": "╝",
    "doble_horizontal": "═",
    "doble_vertical": "║",
    "marca": "■",
    "ok": "✔",
    "error": "✘",
    "aviso": "!",
    "info": "•",
    "proceso": "»",
    "flecha": "›",
    "migas": "›",
    "bloque": "█",
    "pista": "░",
    "sube": "▲",
    "baja": "▼",
    "igual": "=",
    "punto": "·",
}

_SIMBOLOS_ASCII = {
    "sup_izq": "+",
    "sup_der": "+",
    "inf_izq": "+",
    "inf_der": "+",
    "horizontal": "-",
    "vertical": "|",
    "cruce": "+",
    "doble_sup_izq": "+",
    "doble_sup_der": "+",
    "doble_inf_izq": "+",
    "doble_inf_der": "+",
    "doble_horizontal": "=",
    "doble_vertical": "|",
    "marca": "#",
    "ok": "OK",
    "error": "X",
    "aviso": "!",
    "info": "*",
    "proceso": ">>",
    "flecha": ">",
    "migas": ">",
    "bloque": "#",
    "pista": ".",
    "sube": "^",
    "baja": "v",
    "igual": "=",
    "punto": "-",
}


def _color_activo() -> bool:
    """Indica si conviene mostrar colores en la salida actual."""
    if os.environ.get("NO_COLOR"):
        return False

    if os.environ.get("FORCE_COLOR") or os.environ.get("PYCHARM_HOSTED"):
        return True

    if os.environ.get("TERM") == "dumb":
        return False

    try:
        return sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def _unicode_activo() -> bool:
    """Indica si la salida admite los símbolos de dibujo."""
    codificacion = getattr(sys.stdout, "encoding", None) or "ascii"

    try:
        "".join(_SIMBOLOS_UNICODE.values()).encode(codificacion)
    except (UnicodeError, LookupError):
        return False

    return True


def _s(nombre: str) -> str:
    """Devuelve un símbolo de dibujo, con reemplazo ASCII si hace falta."""
    tabla = _SIMBOLOS_UNICODE if _unicode_activo() else _SIMBOLOS_ASCII
    return tabla[nombre]


def _estilo(texto: str, *estilos: str) -> str:
    """Aplica color o negrita a un texto."""
    if not estilos or not _color_activo():
        return texto

    codigos = ";".join(_CODIGOS[nombre] for nombre in estilos)
    return f"\x1b[{codigos}m{texto}\x1b[0m"


def _largo(texto: str) -> int:
    """Largo visible de un texto, sin contar los códigos de color."""
    return len(_ANSI.sub("", texto))


def _ancho() -> int:
    """Ancho útil de la terminal."""
    columnas = shutil.get_terminal_size((80, 24)).columns
    return max(36, min(columnas, 96) - 4)


def _ancho_tabla() -> int:
    """Ancho disponible para tablas (aprovecha terminales anchas)."""
    columnas = shutil.get_terminal_size((80, 24)).columns
    return max(36, columnas - 4)


def _palabra_mas_larga(texto: str) -> int:
    return max((len(palabra) for palabra in texto.split()), default=0)


def _mensaje(simbolo: str, texto: str, color: str, salto: bool) -> None:
    if salto:
        print()

    print(f"  {_estilo(_s(simbolo), color, 'negrita')} {_estilo(texto, color)}")


def _exito(texto: str, salto: bool = True) -> None:
    _mensaje("ok", texto, "verde", salto)


def _error(texto: str, salto: bool = True) -> None:
    _mensaje("error", texto, "rojo", salto)


def _aviso(texto: str, salto: bool = False) -> None:
    _mensaje("aviso", texto, "amarillo", salto)


def _info(texto: str, salto: bool = False) -> None:
    if salto:
        print()

    print(f"  {_estilo(_s('info'), 'cian')} {texto}")


def _nota(texto: str) -> None:
    print("  " + _estilo(texto, "gris"))


def _progreso(texto: str) -> None:
    print()
    print(
        f"  {_estilo(_s('proceso'), 'cian', 'negrita')} "
        f"{_estilo(texto, 'cian')}"
    )


def _titulo_seccion(titulo: str, detalle: str | None = None) -> None:
    linea = _estilo(f"{_s('marca')} {titulo.upper()}", "negrita", "cian")

    if detalle:
        linea += "  " + _estilo(detalle, "gris")

    print()
    print("  " + linea)


def _panel(titulo: str, lineas: list[str], color: str = "cian") -> None:
    """Dibuja un recuadro cerrado adaptado al ancho de la terminal."""
    interior = _ancho() - 2
    espacio_texto = interior - 2
    horizontal = _s("horizontal")
    titulo = titulo.upper()
    if len(titulo) > interior - 3:
        titulo = titulo[:interior - 6] + "..."
    relleno = horizontal * (interior - len(titulo) - 3)

    print()
    print(
        "  "
        + _estilo(_s("sup_izq") + horizontal + " ", color)
        + _estilo(titulo, color, "negrita")
        + " "
        + _estilo(relleno + _s("sup_der"), color)
    )

    for linea in lineas:
        # Las líneas cortas conservan los colores originales. Las largas
        # se distribuyen en renglones para mantener el borde alineado.
        partes = (
            [linea] if _largo(linea) <= espacio_texto else
            textwrap.wrap(
                _ANSI.sub("", linea),
                width=espacio_texto,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]
        )
        for parte in partes:
            espacios = " " * (espacio_texto - _largo(parte))
            print(
                "  " + _estilo(_s("vertical"), color)
                + " " + parte + espacios + " "
                + _estilo(_s("vertical"), color)
            )

    print(
        "  " + _estilo(
            _s("inf_izq") + horizontal * interior + _s("inf_der"),
            color,
        )
    )


def _pares(
    datos: dict[str, Any],
    destacados: dict[str, tuple[str, ...]] | None = None,
) -> list[str]:
    """Arma líneas 'etiqueta  valor' con las etiquetas alineadas."""
    if not datos:
        return []

    destacados = destacados or {}
    ancho = max(len(etiqueta) for etiqueta in datos)
    espacio_valor = max(12, _ancho() - 4 - ancho - 2)
    sangria = " " * (ancho + 2)
    lineas = []

    for etiqueta, valor in datos.items():
        estilos = destacados.get(etiqueta, ("negrita",))
        # Los textos largos siguen en el renglón de abajo; las
        # direcciones web no se cortan para que sigan funcionando.
        partes = textwrap.wrap(
            str(valor),
            espacio_valor,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]

        lineas.append(
            f"{_estilo(etiqueta.ljust(ancho), 'gris')}  "
            f"{_estilo(partes[0], *estilos)}"
        )
        lineas.extend(
            sangria + _estilo(parte, *estilos) for parte in partes[1:]
        )

    return lineas


def _envolver(texto: str, *estilos: str) -> list[str]:
    """Parte un texto largo para que entre dentro de un recuadro."""
    return [
        _estilo(parte, *estilos)
        for parte in textwrap.wrap(texto, max(20, _ancho() - 4)) or [""]
    ]


def _tabla(
    encabezados: list[str],
    filas: list[list[str]],
    estilo_celda: Callable[[int, str], tuple[str, ...]] | None = None,
) -> bool:
    """Dibuja una tabla. Devuelve False si no entra bien en la terminal."""
    columnas = len(encabezados)
    anchos = [
        max([len(encabezados[i])] + [len(fila[i]) for fila in filas])
        for i in range(columnas)
    ]
    minimos = [
        max(
            [_palabra_mas_larga(encabezados[i])]
            + [_palabra_mas_larga(fila[i]) for fila in filas]
        )
        for i in range(columnas)
    ]
    numericas = [
        all(_NUMERO.match(fila[i]) for fila in filas)
        for i in range(columnas)
    ]
    disponible = _ancho_tabla()
    total = 4 + sum(anchos) + 3 * (columnas - 1)

    # Si no entra, se angostan las columnas más anchas y su contenido
    # pasa a varias líneas, sin cortar palabras ni perder información.
    while total > disponible:
        candidatas = [
            i for i in range(columnas)
            if anchos[i] > minimos[i]
        ]

        if not candidatas:
            return False

        mayor = max(candidatas, key=lambda i: anchos[i])
        anchos[mayor] -= 1
        total -= 1

    def partir(texto: str, ancho: int) -> list[str]:
        return textwrap.wrap(
            texto,
            ancho,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]

    # Si alguna celda queda demasiado alta, se lee mejor en fichas.
    if any(
        len(partir(celda, anchos[i])) > 3
        for fila in filas
        for i, celda in enumerate(fila)
    ):
        return False

    horizontal = _s("horizontal")
    separador = _estilo(f" {_s('vertical')} ", "gris")
    union = f"{horizontal}{_s('cruce')}{horizontal}"
    linea = _estilo(
        horizontal
        + union.join(horizontal * ancho for ancho in anchos)
        + horizontal,
        "gris",
    )

    def imprimir(celdas: list[str], estilos: list[tuple[str, ...]]) -> None:
        partes = [
            partir(texto, anchos[i])
            for i, texto in enumerate(celdas)
        ]

        for renglon in range(max(len(parte) for parte in partes)):
            salida = []

            for i, parte in enumerate(partes):
                texto = parte[renglon] if renglon < len(parte) else ""
                ultima = i == columnas - 1

                if numericas[i]:
                    texto = texto.rjust(anchos[i])
                elif not ultima:
                    texto = texto.ljust(anchos[i])

                if texto.strip():
                    texto = _estilo(texto, *estilos[i])

                salida.append(texto)

            print(("   " + separador.join(salida)).rstrip())

    imprimir(encabezados, [("negrita", "cian")] * columnas)
    print("  " + linea)

    hay_ajuste = any(
        len(fila[i]) > anchos[i]
        for fila in filas
        for i in range(columnas)
    )

    for numero, fila in enumerate(filas):
        if hay_ajuste and numero:
            print("  " + linea)

        estilos = [
            estilo_celda(i, celda) if estilo_celda else ()
            for i, celda in enumerate(fila)
        ]
        imprimir(fila, estilos)

    return True


def _barra(proporcion: float, ancho: int, color: str = "cian") -> str:
    """Barra horizontal proporcional a un valor entre 0 y 1."""
    proporcion = min(max(proporcion, 0.0), 1.0)
    llenos = round(proporcion * ancho)

    return (
        _estilo(_s("bloque") * llenos, color)
        + _estilo(_s("pista") * (ancho - llenos), "gris")
    )


def _opcion(numero: str, texto: str, color: str = "cian") -> str:
    return f"{_estilo(numero.rjust(2), color, 'negrita')}  {texto}"


def _menu(
    titulo: str,
    grupos: list[tuple[str, list[tuple[str, ...]]]],
    pie: list[tuple[str, ...]] | None = None,
) -> None:
    """Dibuja un menú; si entra, pone los grupos en columnas."""
    bloques = []

    for nombre, opciones in grupos:
        lineas = [_estilo(nombre.upper(), "gris", "negrita")] if nombre else []
        lineas.extend(_opcion(*opcion) for opcion in opciones)
        bloques.append(lineas)

    anchos = [max(_largo(linea) for linea in bloque) for bloque in bloques]
    espacio = 6
    lineas = []
    necesario = 4 + sum(anchos) + espacio * (len(bloques) - 1)

    if len(bloques) > 1 and necesario <= _ancho():
        for renglon in range(max(len(bloque) for bloque in bloques)):
            partes = []

            for indice, bloque in enumerate(bloques):
                celda = bloque[renglon] if renglon < len(bloque) else ""

                if indice < len(bloques) - 1:
                    celda += " " * (anchos[indice] - _largo(celda) + espacio)

                partes.append(celda)

            lineas.append("".join(partes))
    else:
        for indice, bloque in enumerate(bloques):
            if indice:
                lineas.append("")

            lineas.extend(bloque)

    if pie:
        lineas.append("")
        lineas.extend(_opcion(*opcion) for opcion in pie)

    _panel(titulo, lineas)


def _banner() -> None:
    """Encabezado de bienvenida."""
    interior = min(_ancho() - 4, 58)
    color = "cian"
    borde = _estilo(_s("doble_vertical"), color)
    horizontal = _s("doble_horizontal") * interior

    print()
    print(
        "  " + _estilo(
            _s("doble_sup_izq") + horizontal + _s("doble_sup_der"),
            color,
        )
    )

    for texto, estilos in (
        ("", ()),
        ("B O O K   M A N A G E R", ("negrita",)),
        ("Grupo 44", ("cian", "negrita")),
        ("— Sprint 1 —", ("gris",)),
        ("", ()),
    ):
        print("  " + borde + _estilo(texto.center(interior), *estilos) + borde)

    print(
        "  " + _estilo(
            _s("doble_inf_izq") + horizontal + _s("doble_inf_der"),
            color,
        )
    )


# ======================================================================
# Consola
# ======================================================================


@dataclass(frozen=True)
class Campo:
    """Describe un dato que solicita un formulario."""

    nombre: str
    etiqueta: str
    tipo: str = "texto"
    relacion: str | None = None
    editable: bool = True


@dataclass
class Modelo:
    """Reúne el servicio y el formulario de una entidad."""

    nombre: str
    servicio: Any
    constructor: Callable[..., Any]
    campos: tuple[Campo, ...]
    con_id: bool = True


class Consola:
    """Presenta los menús y comunica las entradas con los servicios."""

    def __init__(
        self,
        generos: ServicioGenero,
        editoriales: ServicioEditorial,
        monedas: ServicioMoneda,
        tipos: ServicioTipoCotizacion,
        libros: ServicioLibro,
        precios: ServicioPrecio,
        stock: ServicioStock,
        cotizaciones: ServicioCotizacionDolar,
    ) -> None:
        self._dolar_visible: Decimal | None = None
        self._referencia_dolar = ""
        self._modelos = {
            "generos": Modelo(
                "Géneros",
                generos,
                entidades.Genero,
                (Campo("nombre", "Nombre"),),
            ),
            "editoriales": Modelo(
                "Editoriales",
                editoriales,
                entidades.Editorial,
                (Campo("nombre", "Nombre"),),
            ),
            "monedas": Modelo(
                "Monedas",
                monedas,
                entidades.Moneda,
                (
                    Campo("codigo", "Código de tres letras"),
                    Campo("nombre", "Nombre"),
                ),
            ),
            "tipos": Modelo(
                "Tipos de cotización",
                tipos,
                entidades.TipoCotizacion,
                (Campo("nombre", "Nombre"),),
            ),
            "libros": Modelo(
                "Libros",
                libros,
                entidades.Libro,
                (
                    Campo("isbn", "ISBN"),
                    Campo("titulo", "Título"),
                    Campo("autor", "Autor"),
                    Campo("editorial", "Editorial", relacion="editoriales"),
                    Campo("genero", "Género", relacion="generos"),
                ),
            ),
            "precios": Modelo(
                "Precios",
                precios,
                entidades.Precio,
                (
                    Campo(
                        "libro",
                        "Libro",
                        relacion="libros",
                        editable=False,
                    ),
                    Campo("moneda", "Moneda", relacion="monedas"),
                    Campo("importe", "Importe", tipo="decimal"),
                ),
            ),
            "stock": Modelo(
                "Stock",
                stock,
                entidades.Stock,
                (
                    Campo(
                        "libro",
                        "Libro",
                        relacion="libros",
                        editable=False,
                    ),
                    Campo("cantidad", "Cantidad", tipo="entero"),
                ),
                con_id=False,
            ),
            "cotizaciones": Modelo(
                "Cotizaciones",
                cotizaciones,
                entidades.CotizacionDolar,
                (
                    Campo(
                        "tipo",
                        "Tipo",
                        relacion="tipos",
                        editable=False,
                    ),
                    Campo(
                        "fecha",
                        "Fecha",
                        tipo="fecha",
                        editable=False,
                    ),
                    Campo("valor", "Pesos por dólar", tipo="decimal"),
                ),
                con_id=False,
            ),
        }

    def _leer(
        self,
        etiqueta: str,
        predeterminado: str | None = None,
    ) -> str:
        """Pide un texto y admite un valor predeterminado."""
        mensaje = (
            f"  {_estilo(_s('flecha'), 'cian', 'negrita')} "
            f"{_estilo(etiqueta, 'negrita')}"
        )

        if predeterminado is not None:
            mensaje += " " + _estilo(f"[{predeterminado}]", "gris")

        texto = input(mensaje + ": ").strip()

        if texto.lower() == "/cancelar":
            raise ValueError("Operación cancelada.")

        if texto == "" and predeterminado is not None:
            return predeterminado

        return texto

    def _pedir_id(
        self,
        etiqueta: str,
        predeterminado: int | None = None,
    ) -> int:
        """Pide un identificador entero positivo."""
        sugerencia = None

        if predeterminado is not None:
            sugerencia = str(predeterminado)

        valor = int(self._leer(etiqueta, sugerencia))

        if valor <= 0:
            raise ValueError("El identificador debe ser mayor que cero.")

        return valor

    def _etiqueta_relacion(self, objeto: Any) -> str:
        """Obtiene un texto breve para una entidad relacionada."""
        if hasattr(objeto, "titulo"):
            return objeto.titulo

        if hasattr(objeto, "nombre"):
            return objeto.nombre

        return str(objeto.id)

    def _actualizar_dolar_visible(self) -> None:
        """Muestra la última cotización oficial guardada, sin consultar internet."""
        oficiales = [
            cotizacion
            for cotizacion in self._modelos["cotizaciones"].servicio.leer_todos()
            if cotizacion.tipo.nombre.strip().casefold()
            in {"oficial", "dólar oficial"}
        ]
        ultima = max(oficiales, key=lambda item: item.fecha, default=None)
        self._dolar_visible = ultima.valor if ultima is not None else None
        self._referencia_dolar = (
            f"Dólar oficial · Última cotización guardada: {ultima.fecha:%d/%m/%Y}"
            if ultima is not None else
            "Dólar oficial: sin cotización guardada."
        )

    def _datos_visibles(
        self,
        modelo: Modelo,
        objeto: Any,
    ) -> dict[str, str]:
        """Convierte los atributos de una entidad en textos legibles."""
        datos = {}

        if modelo.con_id:
            datos["ID"] = str(objeto.id)

        for campo in modelo.campos:
            valor = getattr(objeto, campo.nombre)

            if campo.relacion is not None:
                datos[campo.etiqueta] = (
                    f"{valor.id} - {self._etiqueta_relacion(valor)}"
                )
            elif isinstance(valor, date):
                datos[campo.etiqueta] = valor.isoformat()
            else:
                datos[campo.etiqueta] = str(valor)

        if isinstance(objeto, entidades.Moneda):
            if objeto.codigo == "USD":
                valor = self._dolar_visible
            elif objeto.codigo == "ARS":
                valor = Decimal("1")
            else:
                valor = objeto.cotizacion_ars
            datos["ARS por unidad"] = (
                f"{valor:.2f}" if valor is not None else "Sin cotización"
            )

        return datos

    def _mostrar_detalle(self, modelo: Modelo, objeto: Any) -> None:
        """Muestra todos los campos de un registro."""
        es_dolar = isinstance(objeto, entidades.Moneda) and objeto.codigo == "USD"
        if es_dolar:
            self._actualizar_dolar_visible()
        _panel(modelo.nombre, _pares(self._datos_visibles(modelo, objeto)))
        if es_dolar:
            _nota(self._referencia_dolar)

    def _listar(self, modelo: Modelo) -> None:
        """Muestra todos los registros de una entidad."""
        registros = modelo.servicio.leer_todos()

        muestra_dolar = modelo.constructor is entidades.Moneda and any(
            moneda.codigo == "USD" for moneda in registros
        )
        if muestra_dolar:
            self._actualizar_dolar_visible()

        _titulo_seccion(modelo.nombre, f"{len(registros)} registro(s)")
        if muestra_dolar:
            _nota(self._referencia_dolar)

        if not registros:
            _nota("No hay registros.")
            return

        filas = [self._datos_visibles(modelo, objeto) for objeto in registros]
        encabezados = list(filas[0])
        valores = [list(datos.values()) for datos in filas]

        if _tabla(encabezados, valores):
            return

        # Terminal demasiado angosta: cada registro va en su recuadro.
        for numero, datos in enumerate(filas, start=1):
            _panel(f"{modelo.nombre} {numero}/{len(filas)}", _pares(datos))

    def _pedir_relacion(
        self,
        campo: Campo,
        actual: Any = None,
    ) -> Any:
        """Permite seleccionar una entidad relacionada existente."""
        modelo = self._modelos[campo.relacion]
        self._listar(modelo)

        anterior_id = actual.id if actual is not None else None
        entidad_id = self._pedir_id(
            f"ID de {campo.etiqueta.lower()}",
            anterior_id,
        )

        objeto = modelo.servicio.leer_por_id(entidad_id)

        if objeto is None:
            raise ValueError(
                f"No existe {campo.etiqueta.lower()} con ese identificador."
            )

        return objeto

    def _formulario(
        self,
        modelo: Modelo,
        actual: Any = None,
    ) -> Any:
        """Construye una entidad nueva a partir de las entradas."""
        datos = {}

        _titulo_seccion(
            "Nuevo registro" if actual is None else "Modificar registro",
            modelo.nombre,
        )
        _nota("Escribí /cancelar para abandonar esta operación.")

        if actual is not None:
            _nota("Presioná Enter para conservar el valor mostrado.")

        if modelo.con_id:
            if actual is not None:
                datos["entidad_id"] = actual.id
            else:
                existentes = modelo.servicio.leer_todos()
                siguiente = max(
                    (objeto.id for objeto in existentes),
                    default=0,
                ) + 1
                datos["entidad_id"] = self._pedir_id(
                    "Identificador",
                    siguiente,
                )

        for campo in modelo.campos:
            anterior = (
                getattr(actual, campo.nombre)
                if actual is not None
                else None
            )

            if actual is not None and not campo.editable:
                datos[campo.nombre] = anterior
                continue

            if campo.relacion is not None:
                datos[campo.nombre] = self._pedir_relacion(
                    campo,
                    anterior,
                )
                continue

            sugerencia = str(anterior) if anterior is not None else None
            etiqueta = campo.etiqueta

            if campo.tipo == "fecha":
                etiqueta += " (AAAA-MM-DD)"
            elif campo.tipo == "decimal":
                etiqueta += " (sin separador de miles)"

            texto = self._leer(etiqueta, sugerencia)

            if campo.tipo == "entero":
                valor = int(texto)
            elif campo.tipo == "decimal":
                valor = Decimal(texto.replace(",", "."))
            elif campo.tipo == "fecha":
                valor = date.fromisoformat(texto)
            else:
                valor = texto

            datos[campo.nombre] = valor

        if isinstance(actual, entidades.Moneda):
            mismo_codigo = datos["codigo"].strip().upper() == actual.codigo
            datos["cotizacion_ars"] = (
                actual.cotizacion_ars if mismo_codigo else None
            )

        return modelo.constructor(**datos)

    def _buscar(self, clave: str) -> Any:
        """Busca un registro utilizando la clave de su entidad."""
        modelo = self._modelos[clave]

        if modelo.con_id:
            entidad_id = self._pedir_id("Identificador")
            objeto = modelo.servicio.leer_por_id(entidad_id)
        elif clave == "stock":
            libro_id = self._pedir_id("Identificador del libro")
            objeto = modelo.servicio.leer_por_libro(libro_id)
        else:
            tipo_id = self._pedir_id("Identificador del tipo")
            fecha = date.fromisoformat(
                self._leer("Fecha (AAAA-MM-DD)")
            )
            objeto = modelo.servicio.leer_por_tipo_y_fecha(
                tipo_id,
                fecha,
            )

        if objeto is None:
            raise ValueError("No se encontró el registro.")

        return objeto

    def _eliminar(self, clave: str, objeto: Any) -> bool:
        """Solicita al servicio eliminar el registro seleccionado."""
        modelo = self._modelos[clave]

        if modelo.con_id:
            return modelo.servicio.eliminar(objeto.id)

        if clave == "stock":
            return modelo.servicio.eliminar(objeto.libro.id)

        return modelo.servicio.eliminar(
            objeto.tipo.id,
            objeto.fecha,
        )

    def _submenu(self, clave: str) -> None:
        """Ejecuta el menú CRUD de una entidad."""
        modelo = self._modelos[clave]

        while True:
            _menu(
                f"Menú principal {_s('migas')} {modelo.nombre}",
                [
                    (
                        "",
                        [
                            ("1", "Listar"),
                            ("2", "Crear"),
                            ("3", "Consultar"),
                            ("4", "Modificar"),
                            ("5", "Eliminar", "rojo"),
                        ],
                    ),
                ],
                pie=[("0", "Volver", "gris")],
            )

            try:
                opcion = self._leer("Opción")

                if opcion == "0":
                    return

                if opcion == "1":
                    self._listar(modelo)

                elif opcion == "2":
                    objeto = self._formulario(modelo)
                    creado = modelo.servicio.crear(objeto)
                    _exito("Registro creado.")
                    self._mostrar_detalle(modelo, creado)

                elif opcion == "3":
                    objeto = self._buscar(clave)
                    self._mostrar_detalle(modelo, objeto)

                elif opcion == "4":
                    actual = self._buscar(clave)
                    nuevo = self._formulario(modelo, actual)
                    actualizado = modelo.servicio.actualizar(nuevo)
                    _exito("Registro actualizado.")
                    self._mostrar_detalle(modelo, actualizado)

                elif opcion == "5":
                    objeto = self._buscar(clave)
                    self._mostrar_detalle(modelo, objeto)

                    print()
                    confirmar = self._leer(
                        "¿Confirmás la eliminación? (s/n)",
                        "n",
                    )

                    if confirmar.lower() == "s":
                        eliminado = self._eliminar(clave, objeto)

                        if eliminado:
                            _exito("Registro eliminado.")
                        else:
                            _aviso("El registro ya no existe.", salto=True)
                    else:
                        _info("Eliminación cancelada.", salto=True)

                else:
                    _aviso("Elegí una opción del menú.", salto=True)

            except (
                ValueError,
                InvalidOperation,
                OSError,
                csv.Error,
                KeyError,
            ) as error:
                _error(f"No se pudo completar la operación: {error}")

    def _pedir_cotizacion_para_conversion(
        self, origen: str, destino: str,
    ) -> tuple[int | None, date | None]:
        """Solicita tipo y fecha únicamente cuando interviene el dólar."""
        if origen == destino or "USD" not in {origen, destino}:
            return None, None
        _nota("USD utiliza el tipo y la fecha de su cotización guardada.")
        self._listar(self._modelos["tipos"])
        tipo_id = self._pedir_id("Identificador del tipo de dólar")
        fecha = date.fromisoformat(self._leer("Fecha del dólar (AAAA-MM-DD)"))
        return tipo_id, fecha

    def _convertir_precio(self) -> None:
        """Convierte con tasas fijas y, si corresponde, el histórico del dólar."""
        servicio = self._modelos["precios"].servicio
        self._listar(self._modelos["precios"])
        precio_id = self._pedir_id("Identificador del precio")
        precio = servicio.leer_por_id(precio_id)
        if precio is None:
            raise ValueError("No existe el precio solicitado.")
        self._listar(self._modelos["monedas"])
        moneda_id = self._pedir_id("Identificador de la moneda de destino")
        moneda = self._modelos["monedas"].servicio.leer_por_id(moneda_id)
        if moneda is None:
            raise ValueError("No existe la moneda de destino.")
        tipo_id, fecha = self._pedir_cotizacion_para_conversion(
            precio.moneda.codigo, moneda.codigo
        )
        resultado = servicio.convertir_precio(precio_id, moneda_id, tipo_id, fecha)
        detalle = {
            "Importe original": f"{precio.importe:.2f} {precio.moneda.codigo}",
            "Importe convertido": f"{resultado:.2f} {moneda.codigo}",
        }
        if fecha is not None:
            detalle["Fecha del dólar"] = fecha.isoformat()
        _panel("Conversión de precio", _pares(detalle), "verde")

    def _mostrar_historico(self) -> None:
        """Muestra las cotizaciones de un tipo ordenadas por fecha."""
        self._listar(self._modelos["tipos"])
        tipo_id = self._pedir_id("Identificador del tipo")

        tipo = self._modelos["tipos"].servicio.leer_por_id(tipo_id)

        if tipo is None:
            raise ValueError("No existe ese tipo de cotización.")

        historico = (
            self._modelos["cotizaciones"]
            .servicio.leer_historico_por_tipo(tipo_id)
        )

        _titulo_seccion(f"Histórico: {tipo.nombre}")

        if not historico:
            _nota("No hay cotizaciones registradas.")
            return

        registros = list(historico)
        valores = [cotizacion.valor for cotizacion in registros]
        minimo = min(valores)
        maximo = max(valores)
        ancho_valor = max(len(str(valor)) for valor in valores)
        ancho_barra = max(8, min(30, _ancho() - ancho_valor - 36))
        separador = _estilo(_s("vertical"), "gris")
        anterior = None

        print()

        for cotizacion in registros:
            if maximo > minimo:
                proporcion = float(
                    (cotizacion.valor - minimo) / (maximo - minimo)
                )
            else:
                proporcion = 1.0

            if anterior is None:
                tendencia = " "
            elif cotizacion.valor > anterior:
                tendencia = _estilo(_s("sube"), "amarillo")
            elif cotizacion.valor < anterior:
                tendencia = _estilo(_s("baja"), "cian")
            else:
                tendencia = _estilo(_s("igual"), "gris")

            anterior = cotizacion.valor
            valor = str(cotizacion.valor).rjust(ancho_valor)

            print(
                f"   {cotizacion.fecha.isoformat()} {separador} "
                f"{_estilo(valor, 'negrita')} ARS por USD "
                f"{tendencia} {_barra(0.08 + 0.92 * proporcion, ancho_barra)}"
            )

        print()
        _nota(
            f"Mínimo: {minimo} {_s('punto')} Máximo: {maximo} "
            f"{_s('punto')} Registros: {len(registros)}"
        )

    def mostrar_inventario(self) -> None:
        """Muestra los libros y su cantidad disponible."""
        libros = self._modelos["libros"].servicio.leer_todos()
        servicio_stock = self._modelos["stock"].servicio

        _titulo_seccion("Inventario", f"{len(libros)} libro(s)")

        if not libros:
            _nota("No hay libros registrados.")
            return

        filas = []
        total = 0
        sin_registro = 0

        stock_por_libro = {
            registro.libro.id: registro
            for registro in servicio_stock.leer_todos()
        }

        for libro in libros:
            stock = stock_por_libro.get(libro.id)
            cantidad = (
                str(stock.cantidad)
                if stock is not None
                else "Sin registro"
            )

            if stock is None:
                sin_registro += 1
            else:
                total += stock.cantidad

            filas.append([str(libro.id), libro.titulo, cantidad])

        def color_stock(indice: int, texto: str) -> tuple[str, ...]:
            if indice != 2:
                return ()

            try:
                return (
                    ("verde", "negrita")
                    if int(texto) > 0
                    else ("rojo", "negrita")
                )
            except ValueError:
                return ("gris",)

        if not _tabla(["ID", "Título", "Ejemplares"], filas, color_stock):
            for fila in filas:
                _panel(
                    f"Libro {fila[0]}",
                    _pares(
                        {"Título": fila[1], "Ejemplares": fila[2]},
                        {"Ejemplares": color_stock(2, fila[2])},
                    ),
                )

        print()
        _nota(
            f"Total de ejemplares: {total} {_s('punto')} "
            f"Libros sin registro de stock: {sin_registro}"
        )

    def mostrar_resumen(self) -> None:
        """Muestra la cantidad de registros de cada entidad."""
        _titulo_seccion("Resumen del sistema")

        cantidades = [
            (modelo.nombre, len(modelo.servicio.leer_todos()))
            for modelo in self._modelos.values()
        ]
        mayor = max((cantidad for _, cantidad in cantidades), default=0)
        ancho_nombre = max(len(nombre) for nombre, _ in cantidades)
        ancho_barra = max(8, min(30, _ancho() - ancho_nombre - 16))

        print()

        for nombre, cantidad in cantidades:
            proporcion = cantidad / mayor if mayor else 0.0
            print(
                f"   {nombre.ljust(ancho_nombre)}  "
                f"{_estilo(str(cantidad).rjust(4), 'negrita')}  "
                f"{_barra(proporcion, ancho_barra)}"
            )

        print()
        _nota(
            f"Total: {sum(cantidad for _, cantidad in cantidades)} "
            "registro(s)"
        )

    def _consultar_dolar_online(self) -> None:
        """Consulta DolarAPI y permite guardar el valor de venta."""
        equivalencias = {
            "oficial": "oficial",
            "blue": "blue",
            "mep": "bolsa",
            "bolsa": "bolsa",
            "ccl": "contadoconliqui",
            "contado con liquidación": "contadoconliqui",
            "tarjeta": "tarjeta",
            "mayorista": "mayorista",
            "cripto": "cripto",
        }

        self._listar(self._modelos["tipos"])
        tipo_id = self._pedir_id("Identificador del tipo")

        servicio_tipos = self._modelos["tipos"].servicio
        tipo = servicio_tipos.leer_por_id(tipo_id)

        if tipo is None:
            raise ValueError("No existe ese tipo de cotización.")

        casa = equivalencias.get(tipo.nombre.strip().casefold())

        if casa is None:
            raise ValueError(
                "Ese tipo no tiene una consulta disponible en DolarAPI."
            )

        _progreso("Consultando DolarAPI...")
        externa = ClienteDolarAPI().consultar(casa)

        zona_argentina = timezone(timedelta(hours=-3))
        actualizada = externa.actualizada.astimezone(zona_argentina)
        fecha = actualizada.date()

        _panel(
            "Cotización recibida",
            _pares(
                {
                    "Fuente": "DolarAPI",
                    "Tipo": externa.nombre,
                    "Compra": f"{externa.compra} ARS por USD",
                    "Venta": f"{externa.venta} ARS por USD",
                    "Actualización en Argentina": actualizada.isoformat(),
                },
                {"Venta": ("verde", "negrita")},
            ),
            "verde",
        )
        _nota("Es la última cotización publicada por la fuente.")
        _info(f"Fecha que se guardará: {fecha.isoformat()}")

        servicio = self._modelos["cotizaciones"].servicio
        existente = servicio.leer_por_tipo_y_fecha(tipo.id, fecha)

        if existente is not None:
            _aviso(
                f"Valor ya guardado: {existente.valor} ARS por USD",
                salto=True,
            )

            if existente.valor == externa.venta:
                _info("El valor de venta coincide. No hay cambios.")
                return

            pregunta = "¿Reemplazarlo por el valor de venta recibido? (s/n)"
        else:
            pregunta = "¿Guardar el valor de venta recibido? (s/n)"

        print()
        confirmar = self._leer(pregunta, "n")

        if confirmar.casefold() != "s":
            _info("Consulta finalizada sin modificar los datos.", salto=True)
            return

        cotizacion = entidades.CotizacionDolar(
            tipo,
            fecha,
            externa.venta,
        )

        if existente is None:
            servicio.crear(cotizacion)
            _exito("Cotización creada.")
        else:
            servicio.actualizar(cotizacion)
            _exito("Cotización actualizada.")

        separador = _estilo(_s("vertical"), "gris")
        print(
            f"    {tipo.nombre} {separador} {fecha.isoformat()} {separador} "
            f"{_estilo(str(cotizacion.valor), 'negrita')} ARS por USD"
        )

    def _comparar_precio_cuspide(self) -> None:
        """Compara un precio local con Cúspide utilizando el mismo ISBN."""
        self._listar(self._modelos["precios"])
        precio_id = self._pedir_id("Identificador del precio")

        servicio_precios = self._modelos["precios"].servicio
        precio = servicio_precios.leer_por_id(precio_id)

        if precio is None:
            raise ValueError("No existe ese precio.")

        _panel(
            "Libro local",
            _pares({"Título": precio.libro.titulo, "ISBN": precio.libro.isbn}),
        )
        _progreso("Consultando Cúspide...")

        externo = ClienteCuspideAPI().consultar_por_isbn(
            precio.libro.isbn
        )

        if externo is None:
            _aviso(
                "No se encontró ese ISBN en el catálogo de Cúspide.",
                salto=True,
            )
            _nota("No se realizó la comparación.")
            return

        zona_argentina = timezone(timedelta(hours=-3))
        momento = externo.consultado.astimezone(zona_argentina)

        _panel(
            "Cúspide",
            _pares(
                {
                    "Libro en Cúspide": externo.titulo,
                    "Precio publicado": f"{externo.precio:.2f} ARS",
                    "Disponibilidad informada": (
                        "Con stock" if externo.disponible else "Sin stock"
                    ),
                    "Consulta realizada": momento.isoformat(),
                    "Fuente": externo.url,
                },
                {
                    "Disponibilidad informada": (
                        ("verde", "negrita")
                        if externo.disponible
                        else ("rojo", "negrita")
                    ),
                    "Fuente": ("azul",),
                },
            ),
            "magenta",
        )

        if precio.moneda.codigo == "ARS":
            importe_local = precio.importe
        else:
            monedas = self._modelos["monedas"].servicio.leer_todos()
            pesos = next(
                (moneda for moneda in monedas if moneda.codigo == "ARS"),
                None,
            )

            if pesos is None:
                raise ValueError("Primero registrá la moneda ARS.")

            tipo_id, fecha = self._pedir_cotizacion_para_conversion(
                precio.moneda.codigo, "ARS"
            )
            importe_local = servicio_precios.convertir_precio(
                precio_id, pesos.id, tipo_id, fecha
            )
            if fecha is not None:
                _info(f"Cotización del dólar del día: {fecha.isoformat()}")
            else:
                _nota("Se utilizó la cotización fija de monedas.csv.")

        diferencia = importe_local - externo.precio
        porcentaje = diferencia / externo.precio * Decimal("100")

        lineas = _pares(
            {
                "Precio local original": (
                    f"{precio.importe:.2f} {precio.moneda.codigo}"
                ),
                "Precio local en pesos": f"{importe_local:.2f} ARS",
                "Precio de Cúspide": f"{externo.precio:.2f} ARS",
            }
        )

        mayor = max(importe_local, externo.precio)

        if mayor > 0:
            ancho_barra = max(10, min(32, _ancho() - 40))
            lineas.append("")

            for nombre, importe, color in (
                ("Nosotros", importe_local, "cian"),
                ("Cúspide", externo.precio, "magenta"),
            ):
                lineas.append(
                    f"{_estilo(nombre.ljust(8), 'gris')}  "
                    f"{_barra(float(importe / mayor), ancho_barra, color)}  "
                    f"{importe:.2f} ARS"
                )

        lineas.append("")

        if diferencia > 0:
            lineas.extend(
                _envolver(
                    f"{_s('sube')} Nuestro precio es {diferencia:.2f} ARS "
                    f"más alto ({porcentaje:.2f}% sobre el precio de "
                    "Cúspide).",
                    "amarillo",
                    "negrita",
                )
            )
        elif diferencia < 0:
            lineas.extend(
                _envolver(
                    f"{_s('baja')} Nuestro precio es "
                    f"{abs(diferencia):.2f} ARS más bajo "
                    f"({abs(porcentaje):.2f}% por debajo de Cúspide).",
                    "verde",
                    "negrita",
                )
            )
        else:
            lineas.extend(
                _envolver(
                    f"{_s('igual')} Ambos precios coinciden.",
                    "cian",
                    "negrita",
                )
            )

        _panel("Comparación de precios", lineas)
        _nota("La comparación no incluye gastos de envío.")
        _nota("Los precios guardados no fueron modificados.")

    def ejecutar(self) -> None:
        """Mantiene el menú principal hasta que el usuario sale."""
        claves = list(self._modelos)

        _banner()

        try:
            while True:
                _menu(
                    "Menú principal",
                    [
                        (
                            "Datos",
                            [
                                (str(numero), self._modelos[clave].nombre)
                                for numero, clave in enumerate(
                                    claves,
                                    start=1,
                                )
                            ],
                        ),
                        (
                            "Herramientas",
                            [
                                ("9", "Convertir precio", "magenta"),
                                ("10", "Histórico de cotizaciones", "magenta"),
                                ("11", "Inventario", "magenta"),
                                ("12", "Resumen del sistema", "magenta"),
                                ("13", "Consultar dólar en vivo", "magenta"),
                                ("14", "Comparar con Cúspide en vivo", "magenta"),
                            ],
                        ),
                    ],
                    pie=[("0", "Salir", "rojo")],
                )

                try:
                    opcion = self._leer("Opción")

                    if opcion == "0":
                        print()
                        print("  " + _estilo("Hasta luego.", "cian", "negrita"))
                        print("  " + _estilo("Grupo 44", "cian", "negrita"))
                        print()
                        return

                    if opcion in [str(n) for n in range(1, 9)]:
                        self._submenu(claves[int(opcion) - 1])
                    elif opcion == "9":
                        self._convertir_precio()
                    elif opcion == "10":
                        self._mostrar_historico()
                    elif opcion == "11":
                        self.mostrar_inventario()
                    elif opcion == "12":
                        self.mostrar_resumen()
                    elif opcion == "13":
                        self._consultar_dolar_online()
                    elif opcion == "14":
                        self._comparar_precio_cuspide()
                    else:
                        _aviso("Elegí una opción del menú.", salto=True)

                except (
                    ValueError,
                    InvalidOperation,
                    OSError,
                    csv.Error,
                    KeyError,
                ) as error:
                    _error(f"No se pudo completar la operación: {error}")

        except (EOFError, KeyboardInterrupt):
            print()
            _info("Programa finalizado.")