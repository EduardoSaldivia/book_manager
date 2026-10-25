servicio_scraping = ServicioScraping()
servicio_auditoria = ServicioAuditoria(db)

consola = Consola(**servicios,
                  scraping=servicio_scraping,
                  auditoria=servicio_auditoria)
return Aplicacion(servicios, consola, PrecargaDatos(db), db)