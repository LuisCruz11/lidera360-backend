from app.database.Db import Db
from app.models.dto.Rol_DTO import RolDTO


class RolDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_rol, nombre FROM roles")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [RolDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_rol):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_rol, nombre FROM roles WHERE id_rol = %s", (id_rol,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return RolDTO(*fila)
        return None

    @staticmethod
    def crear(rol_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO roles (nombre) VALUES (%s)", (rol_dto.nombre,))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_rol, rol_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE roles SET nombre = %s WHERE id_rol = %s", (rol_dto.nombre, id_rol))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_rol):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM roles WHERE id_rol = %s", (id_rol,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
