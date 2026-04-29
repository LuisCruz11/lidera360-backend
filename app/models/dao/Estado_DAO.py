from app.database.Db import Db
from app.models.dto.Estado_DTO import EstadoDTO


class EstadoDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_estado, nombre FROM estados")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [EstadoDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_estado):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_estado, nombre FROM estados WHERE id_estado = %s", (id_estado,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return EstadoDTO(*fila)
        return None

    @staticmethod
    def crear(estado_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO estados (nombre) VALUES (%s)", (estado_dto.nombre,))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_estado, estado_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE estados SET nombre = %s WHERE id_estado = %s", (estado_dto.nombre, id_estado))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_estado):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM estados WHERE id_estado = %s", (id_estado,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
