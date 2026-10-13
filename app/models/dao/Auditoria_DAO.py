import pymysql

from app.database.Db import Db
from app.models.dto.Auditoria_DTO import AuditoriaDTO


class AuditoriaDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT a.id_auditoria, a.id_usuario, u.username AS usuario, r.nombre AS rol,
                       a.tabla, a.accion, a.descripcion, a.fecha, a.id_taller, t.nombre AS taller
                FROM auditoria a
                LEFT JOIN usuarios u ON u.id_usuario = a.id_usuario
                LEFT JOIN roles r ON r.id_rol = u.id_rol
                LEFT JOIN taller t ON t.id_taller = a.id_taller
                ORDER BY a.fecha DESC, a.id_auditoria DESC
            """)
            filas = cursor.fetchall()
        finally:
            conexion.close()

        for fila in filas:
            fila["fecha"] = fila["fecha"].isoformat() if fila["fecha"] else None
        return filas

    @staticmethod
    def obtener_por_id(id_auditoria):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_auditoria, id_usuario, tabla, accion, descripcion, fecha, id_taller
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
    def crear(auditoria_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO auditoria (id_usuario, tabla, accion, descripcion, id_taller)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                auditoria_dto.id_usuario,
                auditoria_dto.tabla,
                auditoria_dto.accion,
                auditoria_dto.descripcion,
                auditoria_dto.id_taller
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.lastrowid
        finally:
            if cerrar_conexion:
                conexion.close()
