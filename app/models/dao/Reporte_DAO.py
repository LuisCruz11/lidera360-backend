import pymysql

from app.database.Db import Db


def _personal_del_taller(rol_en_taller):
    """Subconsulta con los nombres del personal asignado al taller `t` con ese rol."""
    return f"""
        (
            SELECT GROUP_CONCAT(
                NULLIF(TRIM(CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, ''))), '')
                ORDER BY p.nombres SEPARATOR ', '
            )
            FROM taller_personal tp
            INNER JOIN personal p ON p.cedula = tp.cedula_personal
            WHERE tp.id_taller = t.id_taller AND LOWER(TRIM(tp.rol_en_taller)) = '{rol_en_taller}'
        )
    """


def _inscripciones_con_estado(condicion_inscripcion, estado):
    """Subconsulta que cuenta inscripciones que cumplen la condición y tienen ese estado."""
    return f"""
        (
            SELECT COUNT(*)
            FROM inscripcion ix
            INNER JOIN estados ex ON ex.id_estado = ix.id_estado
            WHERE {condicion_inscripcion} AND LOWER(ex.nombre) = '{estado}'
        )
    """


def _consultar(sql, parametros=()):
    conexion = Db.obtener_conexion()
    try:
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        conexion.close()


class ReporteDAO:

    @staticmethod
    def clientes_y_progreso():
        return _consultar(f"""
            SELECT c.cedula, c.nombres, c.apellidos, c.correo, c.telefono, c.edad,
                   e.nombre AS estado,
                   tt.nombre AS nivel_actual,
                   (SELECT COUNT(*) FROM inscripcion ix WHERE ix.cliente_cedula = c.cedula) AS inscripciones,
                   {_inscripciones_con_estado("ix.cliente_cedula = c.cedula", "aprobado")} AS aprobados,
                   {_inscripciones_con_estado("ix.cliente_cedula = c.cedula", "no aprobado")} AS no_aprobados,
                   (
                       pc.id_tipo_taller = (SELECT MAX(id_tipo_taller) FROM tipo_taller)
                       AND EXISTS (
                           SELECT 1
                           FROM inscripcion ix
                           INNER JOIN taller tx ON tx.id_taller = ix.id_taller
                           INNER JOIN estados ex ON ex.id_estado = ix.id_estado
                           WHERE ix.cliente_cedula = c.cedula
                             AND tx.id_tipo_taller = pc.id_tipo_taller
                             AND LOWER(ex.nombre) = 'aprobado'
                       )
                   ) AS programa_completado
            FROM clientes c
            LEFT JOIN estados e ON e.id_estado = c.id_estado
            LEFT JOIN progreso_cliente pc ON pc.cliente_cedula = c.cedula
            LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = pc.id_tipo_taller
            ORDER BY c.nombres, c.apellidos
        """)

    @staticmethod
    def inscripciones(fecha_desde=None, fecha_hasta=None, id_taller=None):
        condiciones, parametros = [], []
        if fecha_desde:
            condiciones.append("i.fecha_inscripcion >= %s")
            parametros.append(fecha_desde)
        if fecha_hasta:
            condiciones.append("i.fecha_inscripcion <= %s")
            parametros.append(fecha_hasta)
        if id_taller:
            condiciones.append("i.id_taller = %s")
            parametros.append(id_taller)
        filtro = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        return _consultar(f"""
            SELECT i.fecha_inscripcion, c.cedula, c.nombres, c.apellidos, c.correo,
                   t.nombre AS taller, tt.nombre AS nivel, t.fecha_inicio, t.fecha_fin,
                   {_personal_del_taller("coach")} AS coach,
                   e.nombre AS estado
            FROM inscripcion i
            INNER JOIN clientes c ON c.cedula = i.cliente_cedula
            INNER JOIN taller t ON t.id_taller = i.id_taller
            LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
            LEFT JOIN estados e ON e.id_estado = i.id_estado
            {filtro}
            ORDER BY i.fecha_inscripcion DESC, c.nombres
        """, tuple(parametros))

    @staticmethod
    def talleres():
        return _consultar(f"""
            SELECT t.nombre, tt.nombre AS nivel, t.fecha_inicio, t.fecha_fin, e.nombre AS estado,
                   {_personal_del_taller("coach")} AS coach,
                   {_personal_del_taller("coordinador")} AS coordinador,
                   {_personal_del_taller("personal capacitado")} AS personal_capacitado,
                   (SELECT COUNT(*) FROM inscripcion ix WHERE ix.id_taller = t.id_taller) AS inscritos,
                   {_inscripciones_con_estado("ix.id_taller = t.id_taller", "aprobado")} AS aprobados,
                   {_inscripciones_con_estado("ix.id_taller = t.id_taller", "no aprobado")} AS no_aprobados
            FROM taller t
            LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
            LEFT JOIN estados e ON e.id_estado = t.id_estado
            ORDER BY t.fecha_inicio DESC, t.nombre
        """)

    @staticmethod
    def auditoria(fecha_desde=None, fecha_hasta=None):
        condiciones, parametros = [], []
        if fecha_desde:
            condiciones.append("a.fecha >= %s")
            parametros.append(fecha_desde)
        if fecha_hasta:
            condiciones.append("a.fecha < DATE_ADD(%s, INTERVAL 1 DAY)")
            parametros.append(fecha_hasta)
        filtro = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        return _consultar(f"""
            SELECT a.fecha, u.username AS usuario, r.nombre AS rol,
                   a.tabla, a.accion, a.descripcion, t.nombre AS taller
            FROM auditoria a
            LEFT JOIN usuarios u ON u.id_usuario = a.id_usuario
            LEFT JOIN roles r ON r.id_rol = u.id_rol
            LEFT JOIN taller t ON t.id_taller = a.id_taller
            {filtro}
            ORDER BY a.fecha DESC, a.id_auditoria DESC
        """, tuple(parametros))

    @staticmethod
    def asistencia(id_taller=None):
        filtro = "WHERE i.id_taller = %s" if id_taller else ""
        return _consultar(f"""
            SELECT t.nombre AS taller, t.fecha_inicio, t.fecha_fin,
                   c.cedula, c.nombres, c.apellidos,
                   e.nombre AS estado,
                   (SELECT COUNT(*) FROM asistencia a WHERE a.id_inscripcion = i.id_inscripcion) AS sesiones,
                   (SELECT COALESCE(SUM(a.asistio), 0) FROM asistencia a
                     WHERE a.id_inscripcion = i.id_inscripcion) AS asistencias
            FROM inscripcion i
            INNER JOIN clientes c ON c.cedula = i.cliente_cedula
            INNER JOIN taller t ON t.id_taller = i.id_taller
            LEFT JOIN estados e ON e.id_estado = i.id_estado
            {filtro}
            ORDER BY t.fecha_inicio DESC, t.nombre, c.nombres
        """, (id_taller,) if id_taller else ())
