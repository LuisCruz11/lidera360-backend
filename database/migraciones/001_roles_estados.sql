-- Lidera360 - Migración 001: alinear roles y estados con el código
--
-- El código usa ids fijos de rol (app/utils/auth.py):
--   2 = Coach, 3 = Personal Capacitado, 4 = Cliente, 5 = Coordinador
-- y nombres de estado para inscripciones y talleres
-- ('Iniciado', 'Aprobado', 'No aprobado', 'Finalizado', ...).
--
-- Ejecutar una sola vez sobre la base lidera360.

START TRANSACTION;

-- 1. Roles: renombrar para que coincidan con los ids que usa el código.
--    El id no cambia, por lo que usuarios y personal existentes conservan su rol.
UPDATE roles SET nombre = 'Coach'               WHERE id_rol = 2;
UPDATE roles SET nombre = 'Personal Capacitado' WHERE id_rol = 3;
UPDATE roles SET nombre = 'Cliente'             WHERE id_rol = 4;
UPDATE roles SET nombre = 'Coordinador'         WHERE id_rol = 5;

-- 2. Estados que el sistema necesita además de Activo/Inactivo.
--    'Iniciado' debe quedar con id 3: Cliente_DAO lo usa como respaldo.
INSERT INTO estados (id_estado, nombre) VALUES
  (3, 'Iniciado'),
  (4, 'Aprobado'),
  (5, 'No aprobado'),
  (6, 'Finalizado'),
  (7, 'Planificado'),
  (8, 'En progreso')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- 3. Integridad: evitar inscripciones y asignaciones duplicadas.
ALTER TABLE inscripcion
  ADD UNIQUE KEY uq_inscripcion_cliente_taller (cliente_cedula, id_taller);

ALTER TABLE taller_personal
  ADD UNIQUE KEY uq_taller_personal (id_taller, cedula_personal, rol_en_taller);

COMMIT;

-- 4. Datos de prueba (OPCIONAL, revisar antes de ejecutar):
--    El usuario 'PruebaCoach' quedó con rol 3 (antes "Docente"), que el código trata
--    como Personal Capacitado. Para que entre al panel de Coach:
-- UPDATE personal SET id_rol = 2 WHERE cedula = '1107974839';
-- UPDATE usuarios SET id_rol = 2 WHERE username = 'PruebaCoach';
--
--    El taller 'Prueba1' tiene como coach a un coordinador ('prueba1'), porque el
--    selector de coach no encontraba ningún rol llamado "Coach". Para asignarle el coach real:
-- UPDATE taller_personal SET cedula_personal = '1107974839'
--  WHERE id_taller = 2 AND LOWER(rol_en_taller) = 'coach';
