import pymysql

from app.database.Db import Db
from app.models.dto.Taller_DTO import TallerDTO


class TallerDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_taller, nombre, id_tipo_taller, fecha_inicio, fecha_fin, id_estado FROM taller")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [TallerDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_taller, nombre, id_tipo_taller, fecha_inicio, fecha_fin, id_estado
                FROM taller
                WHERE id_taller = %s
            """, (id_taller,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return TallerDTO(*fila)
        return None

    @staticmethod
    def obtener_detalle(id_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT t.id_taller, t.nombre, t.id_tipo_taller, tt.nombre AS tipo_taller,
                       t.fecha_inicio, t.fecha_fin, t.id_estado, e.nombre AS estado
                FROM taller t
                LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
                LEFT JOIN estados e ON e.id_estado = t.id_estado
                WHERE t.id_taller = %s
            """, (id_taller,))
            taller = cursor.fetchone()

            if not taller:
                return None

            taller["fecha_inicio"] = taller["fecha_inicio"].isoformat() if taller["fecha_inicio"] else None
            taller["fecha_fin"] = taller["fecha_fin"].isoformat() if taller["fecha_fin"] else None

            cursor.execute("""
                SELECT tp.cedula_personal, tp.rol_en_taller, p.nombres, p.apellidos
                FROM taller_personal tp
                INNER JOIN personal p ON p.cedula = tp.cedula_personal
                WHERE tp.id_taller = %s
            """, (id_taller,))
            personal_asignado = cursor.fetchall()

            cursor.execute("""
                SELECT i.id_inscripcion, i.cliente_cedula, c.nombres, c.apellidos,
                       i.id_estado, e.nombre AS estado, i.fecha_inscripcion
                FROM inscripcion i
                INNER JOIN clientes c ON c.cedula = i.cliente_cedula
                LEFT JOIN estados e ON e.id_estado = i.id_estado
                WHERE i.id_taller = %s
                ORDER BY i.fecha_inscripcion DESC
            """, (id_taller,))
            inscritos = cursor.fetchall()

            cursor.execute("""
                SELECT a.id_auditoria, a.descripcion, a.fecha, u.username
                FROM auditoria a
                LEFT JOIN usuarios u ON u.id_usuario = a.id_usuario
                WHERE a.id_taller = %s
                ORDER BY a.fecha DESC
            """, (id_taller,))
            notas = cursor.fetchall()
        finally:
            conexion.close()

        def nombre_completo(fila):
            return f"{fila.get('nombres') or ''} {fila.get('apellidos') or ''}".strip()

        coach = ", ".join(
            nombre_completo(persona) for persona in personal_asignado
            if (persona.get("rol_en_taller") or "").strip().lower() == "coach"
        )
        coordinador = ", ".join(
            nombre_completo(persona) for persona in personal_asignado
            if (persona.get("rol_en_taller") or "").strip().lower() == "coordinador"
        )

        return {
            "taller": taller,
            "coach": coach,
            "coordinador": coordinador,
            "clientes_inscritos": [
                {
                    "id_inscripcion": fila["id_inscripcion"],
                    "cliente_cedula": fila["cliente_cedula"],
                    "nombre": nombre_completo(fila),
                    "id_estado": fila["id_estado"],
                    "estado": fila.get("estado") or "",
                    "fecha_inscripcion": fila["fecha_inscripcion"].isoformat() if fila["fecha_inscripcion"] else None,
                }
                for fila in inscritos
            ],
            "notas": [
                {
                    "id_auditoria": nota["id_auditoria"],
                    "descripcion": nota["descripcion"],
                    "fecha": nota["fecha"].isoformat() if nota["fecha"] else None,
                    "usuario": nota.get("username") or "",
                }
                for nota in notas
            ],
        }

    @staticmethod
    def crear(taller_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO taller (nombre, id_tipo_taller, fecha_inicio, fecha_fin, id_estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                taller_dto.nombre,
                taller_dto.id_tipo_taller,
                taller_dto.fecha_inicio,
                taller_dto.fecha_fin,
                taller_dto.id_estado
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.lastrowid
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(id_taller, taller_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE taller
                SET nombre = %s, id_tipo_taller = %s, fecha_inicio = %s, fecha_fin = %s, id_estado = %s
                WHERE id_taller = %s
            """, (
                taller_dto.nombre,
                taller_dto.id_tipo_taller,
                taller_dto.fecha_inicio,
                taller_dto.fecha_fin,
                taller_dto.id_estado,
                id_taller
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.rowcount > 0
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def eliminar(id_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM taller_personal WHERE id_taller = %s", (id_taller,))
            cursor.execute("DELETE FROM auditoria WHERE id_taller = %s", (id_taller,))
            cursor.execute("DELETE FROM inscripcion WHERE id_taller = %s", (id_taller,))
            cursor.execute("DELETE FROM taller WHERE id_taller = %s", (id_taller,))
            conexion.commit()
            return cursor.rowcount > 0
        except pymysql.err.IntegrityError:
            conexion.rollback()
            raise ValueError(
                "No se puede eliminar el taller porque tiene registros asociados "
                "que no se pudieron eliminar automáticamente."
            )
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
