import secrets

import pymysql

from app.database.Db import Db

ESTADO_APROBADO = 'aprobado'
PREFIJO_CODIGO = 'L360-'


def _generar_codigo():
    return f"{PREFIJO_CODIGO}{secrets.token_hex(4).upper()}"


class CertificadoDAO:

    @staticmethod
    def sincronizar(id_inscripcion, conexion):
        """Mantiene el certificado de una inscripción acorde a su estado:
        Aprobado -> lo emite (o lo reactiva si estaba anulado); otro estado -> lo anula.
        No hace commit: se ejecuta dentro de la transacción de quien lo llama.
        Devuelve el código del certificado vigente, o None."""
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT e.nombre AS estado, c.id_certificado, c.codigo
            FROM inscripcion i
            LEFT JOIN estados e ON e.id_estado = i.id_estado
            LEFT JOIN certificado c ON c.id_inscripcion = i.id_inscripcion
            WHERE i.id_inscripcion = %s
        """, (id_inscripcion,))
        fila = cursor.fetchone()
        if not fila:
            return None

        aprobado = (fila["estado"] or "").strip().lower() == ESTADO_APROBADO

        if not aprobado:
            if fila["id_certificado"]:
                cursor.execute("UPDATE certificado SET anulado = 1 WHERE id_certificado = %s", (fila["id_certificado"],))
            return None

        if fila["id_certificado"]:
            cursor.execute("UPDATE certificado SET anulado = 0 WHERE id_certificado = %s", (fila["id_certificado"],))
            return fila["codigo"]

        codigo = _generar_codigo()
        cursor.execute("""
            INSERT INTO certificado (id_inscripcion, codigo)
            VALUES (%s, %s)
        """, (id_inscripcion, codigo))
        return codigo

    @staticmethod
    def _consulta_detalle(condicion):
        return f"""
            SELECT ce.id_certificado, ce.codigo, ce.fecha_emision, ce.anulado,
                   i.id_inscripcion, i.cliente_cedula,
                   cl.nombres, cl.apellidos,
                   t.nombre AS taller, t.fecha_inicio, t.fecha_fin,
                   tt.nombre AS nivel,
                   (
                       SELECT GROUP_CONCAT(
                           NULLIF(TRIM(CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, ''))), '')
                           SEPARATOR ', '
                       )
                       FROM taller_personal tp
                       INNER JOIN personal p ON p.cedula = tp.cedula_personal
                       WHERE tp.id_taller = t.id_taller AND LOWER(TRIM(tp.rol_en_taller)) = 'coach'
                   ) AS coach
            FROM certificado ce
            INNER JOIN inscripcion i ON i.id_inscripcion = ce.id_inscripcion
            INNER JOIN clientes cl ON cl.cedula = i.cliente_cedula
            INNER JOIN taller t ON t.id_taller = i.id_taller
            LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
            WHERE {condicion}
        """

    @staticmethod
    def obtener_vigente_de_cliente(cedula, id_inscripcion):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                CertificadoDAO._consulta_detalle("i.id_inscripcion = %s AND i.cliente_cedula = %s AND ce.anulado = 0"),
                (id_inscripcion, cedula)
            )
            return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_codigo(codigo):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute(CertificadoDAO._consulta_detalle("ce.codigo = %s"), (codigo,))
            return cursor.fetchone()
        finally:
            conexion.close()
