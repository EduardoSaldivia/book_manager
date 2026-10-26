-- Datos de origen del Sprint 1. Ejecutar archivos en orden.
-- Las claves existentes se conservan sin reemplazar.
BEGIN;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (1, '2026-09-28', 1200.00, 1200.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (2, '2026-09-28', 1250.00, 1250.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (3, '2026-09-28', 1230.00, 1230.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (4, '2026-09-28', 1240.00, 1240.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (5, '2026-09-28', 1560.00, 1560.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (6, '2026-09-28', 1180.00, 1180.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (7, '2026-09-28', 1260.00, 1260.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (8, '2026-09-28', 1100.00, 1100.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (9, '2026-09-28', 1150.00, 1150.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

INSERT INTO cotizaciones (tipo_id, fecha, compra, venta)
VALUES (10, '2026-09-28', 1300.00, 1300.00)
ON CONFLICT (tipo_id, fecha) DO NOTHING;

COMMIT;