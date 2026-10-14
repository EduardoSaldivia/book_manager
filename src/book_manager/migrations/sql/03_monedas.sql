-- Datos de origen del Sprint 1. Ejecutar archivos en orden.
-- Las claves existentes se conservan sin reemplazar.
BEGIN;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (1, 'ARS', 'Peso argentino', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (2, 'USD', 'Dólar estadounidense', NULL) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (3, 'EUR', 'Euro', 1736.292041) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (4, 'BRL', 'Real brasileño', 293.414996) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (5, 'CLP', 'Peso chileno', 1.578956) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (6, 'UYU', 'Peso uruguayo', 37.848501) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (7, 'GBP', 'Libra esterlina', 2021.684029) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (8, 'CHF', 'Franco suizo', 1836.443416) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (9, 'JPY', 'Yen japonés', 9.676321) ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, cotizacion_ars) VALUES (10, 'CAD', 'Dólar canadiense', 1077.321264) ON CONFLICT (id) DO NOTHING;
COMMIT;
