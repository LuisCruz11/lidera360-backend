import pymysql

from app.database.Db import Db
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO

ESTADO_APROBADO = 'aprobado'


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
    def actualizar(id_progreso, progreso_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
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
            if cerrar_conexion:
                conexion.commit()
            return cursor.rowcount > 0
        finally:
            if cerrar_conexion:
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

    @staticmethod
    def avanzar_si_aprobo(id_inscripcion, id_usuario, conexion):
        """Sube al cliente al siguiente nivel si la inscripción quedó Aprobada en un
        taller de su nivel actual. Los niveles se ordenan por id_tipo_taller.
        No hace commit: se ejecuta dentro de la transacción de quien lo llama.
        Devuelve el nombre del nuevo nivel, o None si el nivel no cambió."""
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT i.cliente_cedula, i.id_taller, e.nombre AS estado, t.id_tipo_taller,
                   pc.id_progreso, pc.id_tipo_taller AS nivel_actual, tt.nombre AS nombre_nivel_actual
            FROM inscripcion i
            INNER JOIN taller t ON t.id_taller = i.id_taller
            LEFT JOIN estados e ON e.id_estado = i.id_estado
            LEFT JOIN progreso_cliente pc ON pc.cliente_cedula = i.cliente_cedula
            LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = pc.id_tipo_taller
            WHERE i.id_inscripcion = %s
        """, (id_inscripcion,))
        fila = cursor.fetchone()

        if not fila or not fila["id_progreso"]:
            return None
        if (fila["estado"] or "").strip().lower() != ESTADO_APROBADO:
            return None
        if fila["id_tipo_taller"] != fila["nivel_actual"]:
            return None

        cursor.execute("""
            SELECT id_tipo_taller, nombre
            FROM tipo_taller
            WHERE id_tipo_taller > %s
            ORDER BY id_tipo_taller ASC
            LIMIT 1
        """, (fila["nivel_actual"],))
        siguiente = cursor.fetchone()
        if not siguiente:
            return None

        cursor.execute("""
            UPDATE progreso_cliente
            SET id_tipo_taller = %s
            WHERE id_progreso = %s
        """, (siguiente["id_tipo_taller"], fila["id_progreso"]))
        cursor.execute("""
            INSERT INTO auditoria (id_usuario, tabla, accion, descripcion, id_taller)
            VALUES (%s, 'progreso_cliente', 'avance_nivel', %s, %s)
        """, (
            id_usuario,
            f"El cliente {fila['cliente_cedula']} avanzó de {fila['nombre_nivel_actual']} a {siguiente['nombre']}",
            fila["id_taller"]
        ))
        return siguiente["nombre"]
