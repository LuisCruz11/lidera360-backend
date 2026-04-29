from app.database.Db import Db
from app.models.dto.Auditoria_DTO import AuditoriaDTO


class AuditoriaDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_auditoria, id_usuario, tabla, accion, descripcion, fecha FROM auditoria")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [AuditoriaDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_auditoria):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_auditoria, id_usuario, tabla, accion, descripcion, fecha
                FROM auditoria
                WHERE id_auditoria = %s
            """, (id_auditoria,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return AuditoriaDTO(*fila)
        return None

    @staticmethod
    def crear(auditoria_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO auditoria (id_usuario, tabla, accion, descripcion)
                VALUES (%s, %s, %s, %s)
            """, (
                auditoria_dto.id_usuario,
                auditoria_dto.tabla,
                auditoria_dto.accion,
                auditoria_dto.descripcion
            ))
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_auditoria, auditoria_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE auditoria
                SET id_usuario = %s, tabla = %s, accion = %s, descripcion = %s
                WHERE id_auditoria = %s
            """, (
                auditoria_dto.id_usuario,
                auditoria_dto.tabla,
                auditoria_dto.accion,
                auditoria_dto.descripcion,
                id_auditoria
            ))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_auditoria):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM auditoria WHERE id_auditoria = %s", (id_auditoria,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
