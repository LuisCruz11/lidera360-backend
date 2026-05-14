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
    def crear(inscripcion_dto):
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
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_inscripcion, inscripcion_dto):
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
            conexion.commit()
            return cursor.rowcount > 0
        finally:
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
