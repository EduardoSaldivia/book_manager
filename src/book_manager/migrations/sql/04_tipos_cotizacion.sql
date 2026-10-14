-- Datos de origen del Sprint 1. Ejecutar archivos en orden.
-- Las claves existentes se conservan sin reemplazar.
BEGIN;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (1, 'Oficial') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (2, 'Blue') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (3, 'MEP') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (4, 'CCL') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (5, 'Tarjeta') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (6, 'Mayorista') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (7, 'Cripto') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (8, 'Ahorro') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (9, 'Agro') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (10, 'Turista') ON CONFLICT (id) DO NOTHING;
COMMIT;
