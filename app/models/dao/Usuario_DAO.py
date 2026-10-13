from app.database.Db import Db
from app.models.dto.Usuario_DTO import UsuarioDTO
import bcrypt
import pymysql

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
    def obtener_por_correo(correo):
        """Usuario activo cuyo cliente o personal vinculado tiene ese correo.
        Devuelve (UsuarioDTO, nombre, correo) o None."""
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT u.id_usuario, u.username, u.password, u.id_rol, u.cedula_personal, u.activo, u.cedula_cliente,
                       COALESCE(c.nombres, p.nombres, u.username) AS nombre,
                       COALESCE(c.correo, p.correo) AS correo
                FROM usuarios u
                LEFT JOIN clientes c ON c.cedula = u.cedula_cliente
                LEFT JOIN personal p ON p.cedula = u.cedula_personal
                WHERE u.activo = 1 AND (LOWER(c.correo) = LOWER(%s) OR LOWER(p.correo) = LOWER(%s))
                LIMIT 1
            """, (correo, correo))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if not fila:
            return None
        return UsuarioDTO(*fila[:7]), fila[7], fila[8]

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
    def actualizar_password(id_usuario, password_cifrado):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE usuarios SET password = %s WHERE id_usuario = %s",
                (password_cifrado, id_usuario)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_usuario):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM auditoria WHERE id_usuario = %s", (id_usuario,))
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            conexion.commit()
            return cursor.rowcount > 0
        except pymysql.err.IntegrityError:
            conexion.rollback()
            raise ValueError(
                "No se puede eliminar el usuario porque tiene registros asociados "
                "que no se pudieron eliminar automáticamente."
            )
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
