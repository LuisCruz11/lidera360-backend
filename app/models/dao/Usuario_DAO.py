from app.database.Db import Db
from app.models.dto.Usuario_DTO import UsuarioDTO
import bcrypt

class UsuarioDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario, username, password, id_rol, cedula_personal, activo, cedula_cliente FROM usuarios")
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
                SELECT id_usuario, username, password, id_rol, cedula_personal, activo, cedula_cliente
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
    def obtener_por_username(username):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_usuario, username, password, id_rol, cedula_personal, activo, cedula_cliente
                FROM usuarios
                WHERE username = %s
            """, (username,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return UsuarioDTO(*fila)
        return None

    @staticmethod
    def obtener_por_cedula_personal(cedula_personal):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_usuario, username, password, id_rol, cedula_personal, activo, cedula_cliente
                FROM usuarios
                WHERE cedula_personal = %s
            """, (cedula_personal,))
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
                SELECT id_usuario, username, password, id_rol, cedula_personal, activo, cedula_cliente
                FROM usuarios
                WHERE username = %s AND activo = 1
            """, (username,))

            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:

            password_db = fila[2].encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), password_db):
                return UsuarioDTO(*fila)

        return None

    @staticmethod
    def crear(usuario_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios (username, password, id_rol, cedula_personal, activo, cedula_cliente)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                usuario_dto.username,
                usuario_dto.password,
                usuario_dto.id_rol,
                usuario_dto.cedula_personal,
                usuario_dto.activo,
                usuario_dto.cedula_cliente
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.lastrowid
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(id_usuario, usuario_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET username = %s, password = %s, id_rol = %s, cedula_personal = %s, activo = %s, cedula_cliente = %s
                WHERE id_usuario = %s
            """, (
                usuario_dto.username,
                usuario_dto.password,
                usuario_dto.id_rol,
                usuario_dto.cedula_personal,
                usuario_dto.activo,
                usuario_dto.cedula_cliente,
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
