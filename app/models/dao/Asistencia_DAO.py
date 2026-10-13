import pymysql

from app.database.Db import Db


class AsistenciaDAO:

    @staticmethod
    def obtener_por_taller_y_fecha(id_taller, fecha):
        """Lista los inscritos del taller con su asistencia en `fecha` (None si aún no se registró)
        y su acumulado: sesiones registradas y sesiones asistidas."""
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT i.id_inscripcion, i.cliente_cedula, c.nombres, c.apellidos,
                       e.nombre AS estado, a.asistio,
                       (SELECT COUNT(*) FROM asistencia ax WHERE ax.id_inscripcion = i.id_inscripcion) AS sesiones,
                       (SELECT COALESCE(SUM(ax.asistio), 0) FROM asistencia ax
                         WHERE ax.id_inscripcion = i.id_inscripcion) AS asistencias
                FROM inscripcion i
                INNER JOIN clientes c ON c.cedula = i.cliente_cedula
                LEFT JOIN estados e ON e.id_estado = i.id_estado
                LEFT JOIN asistencia a ON a.id_inscripcion = i.id_inscripcion AND a.fecha = %s
                WHERE i.id_taller = %s
                ORDER BY c.nombres ASC, c.apellidos ASC
            """, (fecha, id_taller))
            filas = cursor.fetchall()
        finally:
            conexion.close()

        return [
            {
                "id_inscripcion": fila["id_inscripcion"],
                "cliente_cedula": fila["cliente_cedula"],
                "nombre": f"{fila.get('nombres') or ''} {fila.get('apellidos') or ''}".strip(),
                "estado": fila.get("estado") or "",
                "asistio": None if fila["asistio"] is None else bool(fila["asistio"]),
                "sesiones": int(fila["sesiones"] or 0),
                "asistencias": int(fila["asistencias"] or 0),
            }
            for fila in filas
        ]

    @staticmethod
    def guardar(id_taller, fecha, registros, id_usuario):
        """Registra (o corrige) la asistencia de varios inscritos del taller para una fecha.
        `registros` es una lista de (id_inscripcion, asistio). Devuelve (presentes, total)."""
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_inscripcion FROM inscripcion WHERE id_taller = %s", (id_taller,))
            inscripciones_del_taller = {fila[0] for fila in cursor.fetchall()}

            ajenas = [id_inscripcion for id_inscripcion, _ in registros if id_inscripcion not in inscripciones_del_taller]
            if ajenas:
                raise ValueError("Hay inscripciones que no pertenecen a este taller")

            cursor.executemany("""
                INSERT INTO asistencia (id_inscripcion, fecha, asistio, id_usuario)
                VALUES (%s, %s, %s, %s) AS nuevo
                ON DUPLICATE KEY UPDATE asistio = nuevo.asistio, id_usuario = nuevo.id_usuario
            """, [(id_inscripcion, fecha, int(asistio), id_usuario) for id_inscripcion, asistio in registros])

            presentes = sum(1 for _, asistio in registros if asistio)
            cursor.execute("""
                INSERT INTO auditoria (id_usuario, tabla, accion, descripcion, id_taller)
                VALUES (%s, 'asistencia', 'asistencia', %s, %s)
            """, (
                id_usuario,
                f"Asistencia del {fecha}: {presentes} de {len(registros)} participantes presentes",
                id_taller
            ))
            conexion.commit()
            return presentes, len(registros)
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
