from app.database.Db import Db
from app.models.dto.Taller_Personal_DTO import TallerPersonalDTO


class TallerPersonalDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_taller_personal, id_taller, cedula_personal, id_rol
                FROM taller_personal
            """)
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [TallerPersonalDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_taller_personal):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_taller_personal, id_taller, cedula_personal, id_rol
                FROM taller_personal
                WHERE id_taller_personal = %s
            """, (id_taller_personal,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return TallerPersonalDTO(*fila)
        return None

    @staticmethod
    def crear(taller_personal_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO taller_personal (id_taller, cedula_personal, id_rol)
                VALUES (%s, %s, %s)
            """, (
                taller_personal_dto.id_taller,
                taller_personal_dto.cedula_personal,
                taller_personal_dto.id_rol
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.lastrowid
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(id_taller_personal, taller_personal_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE taller_personal
                SET id_taller = %s, cedula_personal = %s, id_rol = %s
                WHERE id_taller_personal = %s
            """, (
                taller_personal_dto.id_taller,
                taller_personal_dto.cedula_personal,
                taller_personal_dto.id_rol,
                id_taller_personal
            ))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_taller_personal):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM taller_personal WHERE id_taller_personal = %s", (id_taller_personal,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
