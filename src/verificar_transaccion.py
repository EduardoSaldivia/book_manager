from book_manager.database.connection import ConexionDB
from book_manager.models.models import GeneroModelo


class ErrorDePrueba(Exception):
    """Error intencional para comprobar el rollback."""


def verificar_rollback() -> None:
    db = ConexionDB()
    id_prueba = 2147483647

    try:
        try:
            with db.transaccion() as sesion:
                if sesion.get(GeneroModelo, id_prueba) is not None:
                    raise ValueError(
                        "El ID de prueba ya esta ocupado. "
                        "No se modifico ese registro."
                    )

                genero = GeneroModelo(
                    id=id_prueba,
                    nombre="Prueba de rollback",
                )
                sesion.add(genero)

                # Envia la insercion, pero todavia no la confirma.
                sesion.flush()
                print("Insercion enviada, pendiente de confirmacion.")

                # Simula un fallo dentro de la transaccion.
                raise ErrorDePrueba("Fallo intencional.")

        except ErrorDePrueba:
            print("Error simulado: la transaccion fue revertida.")

        with db.transaccion() as sesion:
            registro = sesion.get(GeneroModelo, id_prueba)
            if registro is not None:
                raise AssertionError(
                    "Fallo la prueba: el registro quedo guardado."
                )

        print("OK: el genero de prueba no quedo guardado.")

    finally:
        db.cerrar()


if __name__ == "__main__":
    verificar_rollback()
