-- Datos de origen del Sprint 1. Ejecutar archivos en orden.
-- Las claves existentes se conservan sin reemplazar.
BEGIN;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (1, '2026-09-28', 1200.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (2, '2026-09-28', 1250.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (3, '2026-09-28', 1230.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (4, '2026-09-28', 1240.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (5, '2026-09-28', 1560.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (6, '2026-09-28', 1180.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (7, '2026-09-28', 1260.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (8, '2026-09-28', 1100.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (9, '2026-09-28', 1150.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
INSERT INTO cotizaciones (tipo_id, fecha, valor) VALUES (10, '2026-09-28', 1300.00) ON CONFLICT (tipo_id, fecha) DO NOTHING;
COMMIT;
