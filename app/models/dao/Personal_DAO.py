from app.database.Db import Db
from app.models.dto.Personal_DTO import PersonalDTO
import pymysql


class PersonalDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT cedula, nombres, apellidos, correo, telefono, id_rol FROM personal")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [PersonalDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_cedula(cedula):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT cedula, nombres, apellidos, correo, telefono, id_rol
                FROM personal
                WHERE cedula = %s
            """, (cedula,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return PersonalDTO(*fila)
        return None

    @staticmethod
    def crear(personal_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO personal (cedula, nombres, apellidos, correo, telefono, id_rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                personal_dto.cedula,
                personal_dto.nombres,
                personal_dto.apellidos,
                personal_dto.correo,
                personal_dto.telefono,
                personal_dto.id_rol
            ))
            if cerrar_conexion:
                conexion.commit()
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(cedula, personal_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE personal
                SET nombres = %s, apellidos = %s, correo = %s, telefono = %s, id_rol = %s
                WHERE cedula = %s
            """, (
                personal_dto.nombres,
                personal_dto.apellidos,
                personal_dto.correo,
                personal_dto.telefono,
                personal_dto.id_rol,
                cedula
            ))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(cedula):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario FROM usuarios WHERE cedula_personal = %s", (cedula,))
            usuario = cursor.fetchone()

            cursor.execute("DELETE FROM taller_personal WHERE cedula_personal = %s", (cedula,))
            if usuario:
                cursor.execute("DELETE FROM auditoria WHERE id_usuario = %s", (usuario[0],))
                cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (usuario[0],))
            cursor.execute("DELETE FROM personal WHERE cedula = %s", (cedula,))
            conexion.commit()
            return cursor.rowcount > 0
        except pymysql.err.IntegrityError:
            conexion.rollback()
            raise ValueError(
                "No se puede eliminar el personal porque tiene registros asociados "
                "que no se pudieron eliminar automáticamente."
            )
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
