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
    def actualizar(id_taller, taller_dto):
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
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM taller WHERE id_taller = %s", (id_taller,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
