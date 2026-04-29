from app.database.Db import Db
from app.models.dto.Usuario_DTO import UsuarioDTO


class UsuarioDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario, username, password, id_rol, cedula_personal, activo FROM usuarios")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [UsuarioDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_usuario):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_usuario, username, password, id_rol, cedula_personal, activo
                FROM usuarios
                WHERE id_usuario = %s
            """, (id_usuario,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return UsuarioDTO(*fila)
        return None

    @staticmethod
    def login(username, password):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_usuario, username, password, id_rol, cedula_personal, activo
                FROM usuarios
                WHERE username = %s AND password = %s AND activo = 1
            """, (username, password))

            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return UsuarioDTO(*fila)
        return None

    @staticmethod
    def crear(usuario_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios (username, password, id_rol, cedula_personal, activo)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                usuario_dto.username,
                usuario_dto.password,
                usuario_dto.id_rol,
                usuario_dto.cedula_personal,
                usuario_dto.activo
            ))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_usuario, usuario_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET username = %s, password = %s, id_rol = %s, cedula_personal = %s, activo = %s
                WHERE id_usuario = %s
            """, (
                usuario_dto.username,
                usuario_dto.password,
                usuario_dto.id_rol,
                usuario_dto.cedula_personal,
                usuario_dto.activo,
                id_usuario
            ))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_usuario):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
