from app.database.Db import Db
from app.models.dto.Personal_DTO import PersonalDTO


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
            cursor.execute("DELETE FROM personal WHERE cedula = %s", (cedula,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
