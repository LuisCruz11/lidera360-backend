from app.database.Db import Db
from app.models.dto.Tipo_Taller_DTO import TipoTallerDTO


class TipoTallerDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_tipo_taller, nombre FROM tipo_taller")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [TipoTallerDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_tipo_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_tipo_taller, nombre
                FROM tipo_taller
                WHERE id_tipo_taller = %s
            """, (id_tipo_taller,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return TipoTallerDTO(*fila)
        return None

    @staticmethod
    def crear(tipo_taller_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO tipo_taller (nombre) VALUES (%s)", (tipo_taller_dto.nombre,))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_tipo_taller, tipo_taller_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE tipo_taller
                SET nombre = %s
                WHERE id_tipo_taller = %s
            """, (tipo_taller_dto.nombre, id_tipo_taller))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_tipo_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM tipo_taller WHERE id_tipo_taller = %s", (id_tipo_taller,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
