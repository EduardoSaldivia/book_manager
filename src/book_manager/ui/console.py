    def _ejecutar_scraping(self):
        umbral = self._leer("Diferencia mínima para alerta en ARS")
        resultado = self._scraping.ejecutar_scraping(umbral)
        print(
            f"Libros revisados: {resultado['libros']} | "
            f"Alertas: {resultado['alertas']}"
        )
        print(f"CSV para analizar: {resultado['csv']}")

    def _generar_reporte_excel(self):
        ruta = self._scraping.generar_reporte_excel()
        print(f"Reporte Excel: {ruta}")

    def _mostrar_historial_auditoria(self):
        filas = self._auditoria.leer_historico()
        if not filas:
            print("Todavía no hay operaciones auditadas.")
            return
        for fila in filas:
            print(f"{fila.fecha} | {fila.accion} | {fila.detalles}")

("18", "Ejecutar scraping", "magenta"),
("19", "Generar reporte Excel", "magenta"),
("20", "Ver historial de auditoría", "magenta"),

# En el bloque que atiende la opción elegida:
elif opcion == "18":
    self._ejecutar_scraping()
elif opcion == "19":
    self._generar_reporte_excel()
elif opcion == "20":
    self._mostrar_historial_auditoria()