-- Datos de origen del Sprint 1. Ejecutar archivos en orden.
-- Las claves existentes se conservan sin reemplazar.
BEGIN;
INSERT INTO generos (id, nombre) VALUES (1, 'Novela') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (2, 'Ensayo') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (3, 'Cuento') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (4, 'Infantil') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (5, 'Ciencia ficción') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (6, 'Fantasía') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (7, 'Historia') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (8, 'Biografía') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (9, 'Juvenil') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (10, 'Policial') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (11, 'Romántica') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (12, 'Autoayuda') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (13, 'Psicología') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (14, 'Divulgación científica') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (15, 'Historieta') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (16, 'Pasatiempos') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (17, 'Deportes') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (18, 'Negocios') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (19, 'Crónica') ON CONFLICT (id) DO NOTHING;
COMMIT;
