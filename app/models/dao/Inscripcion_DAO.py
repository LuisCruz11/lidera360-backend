import pymysql

from app.database.Db import Db
from app.models.dto.Inscripcion_DTO import InscripcionDTO


class InscripcionDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_inscripcion, cliente_cedula, id_taller, id_estado, fecha_inscripcion
                FROM inscripcion
            """)
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [InscripcionDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_inscripcion):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_inscripcion, cliente_cedula, id_taller, id_estado, fecha_inscripcion
                FROM inscripcion
                WHERE id_inscripcion = %s
            """, (id_inscripcion,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return InscripcionDTO(*fila)
        return None

    @staticmethod
    def obtener_datos_notificacion(id_inscripcion):
        """Datos para notificar al cliente sobre su inscripción: destinatario, taller, estado y coach."""
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT c.nombres, c.correo,
                       t.nombre AS taller, t.fecha_inicio, t.fecha_fin,
                       tt.nombre AS nivel,
                       e.nombre AS estado,
                       t.id_tipo_taller = (SELECT MAX(id_tipo_taller) FROM tipo_taller) AS es_ultimo_nivel,
                       (
                           SELECT GROUP_CONCAT(
                               NULLIF(TRIM(CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, ''))), '')
                               SEPARATOR ', '
                           )
                           FROM taller_personal tp
                           INNER JOIN personal p ON p.cedula = tp.cedula_personal
                           WHERE tp.id_taller = t.id_taller AND LOWER(TRIM(tp.rol_en_taller)) = 'coach'
                       ) AS coach
                FROM inscripcion i
                INNER JOIN clientes c ON c.cedula = i.cliente_cedula
                INNER JOIN taller t ON t.id_taller = i.id_taller
                LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
                LEFT JOIN estados e ON e.id_estado = i.id_estado
                WHERE i.id_inscripcion = %s
            """, (id_inscripcion,))
            return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def existe(cliente_cedula, id_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_inscripcion
                FROM inscripcion
                WHERE cliente_cedula = %s AND id_taller = %s
                LIMIT 1
            """, (cliente_cedula, id_taller))
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    @staticmethod
    def crear(inscripcion_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO inscripcion (cliente_cedula, id_taller, id_estado, fecha_inscripcion)
                VALUES (%s, %s, %s, %s)
            """, (
                inscripcion_dto.cliente_cedula,
                inscripcion_dto.id_taller,
                inscripcion_dto.id_estado,
                inscripcion_dto.fecha_inscripcion
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.lastrowid
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(id_inscripcion, inscripcion_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE inscripcion
                SET cliente_cedula = %s, id_taller = %s, id_estado = %s, fecha_inscripcion = %s
                WHERE id_inscripcion = %s
            """, (
                inscripcion_dto.cliente_cedula,
                inscripcion_dto.id_taller,
                inscripcion_dto.id_estado,
                inscripcion_dto.fecha_inscripcion,
                id_inscripcion
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.rowcount > 0
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar_estado(id_inscripcion, id_estado, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE inscripcion
                SET id_estado = %s
                WHERE id_inscripcion = %s
            """, (id_estado, id_inscripcion))
            if cerrar_conexion:
                conexion.commit()
            return cursor.rowcount > 0
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def eliminar(id_inscripcion):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM inscripcion WHERE id_inscripcion = %s", (id_inscripcion,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
