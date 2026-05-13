from app.database.Db import Db
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO


class ProgresoClienteDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_progreso, cliente_cedula, id_tipo_taller FROM progreso_cliente")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [ProgresoClienteDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_progreso):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_progreso, cliente_cedula, id_tipo_taller
                FROM progreso_cliente
                WHERE id_progreso = %s
            """, (id_progreso,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return ProgresoClienteDTO(*fila)
        return None

    @staticmethod
    def obtener_por_cliente(cliente_cedula):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_progreso, cliente_cedula, id_tipo_taller
                FROM progreso_cliente
                WHERE cliente_cedula = %s
            """, (cliente_cedula,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return ProgresoClienteDTO(*fila)
        return None

    @staticmethod
    def crear(progreso_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO progreso_cliente (cliente_cedula, id_tipo_taller)
                VALUES (%s, %s)
            """, (
                progreso_dto.cliente_cedula,
                progreso_dto.id_tipo_taller
            ))
            if cerrar_conexion:
                conexion.commit()
            return cursor.lastrowid
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(id_progreso, progreso_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE progreso_cliente
                SET cliente_cedula = %s, id_tipo_taller = %s
                WHERE id_progreso = %s
            """, (
                progreso_dto.cliente_cedula,
                progreso_dto.id_tipo_taller,
                id_progreso
            ))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_progreso):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM progreso_cliente WHERE id_progreso = %s", (id_progreso,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
