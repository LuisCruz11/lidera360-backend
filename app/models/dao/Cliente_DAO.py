from app.database.Db import Db
from app.models.dto.Cliente_DTO import ClienteDTO
import pymysql


class ClienteDAO:

    @staticmethod
    def _fecha_iso(valor):
        return valor.isoformat() if hasattr(valor, "isoformat") else valor

    @staticmethod
    def _taller_panel_desde_fila(fila):
        return {
            "id_inscripcion": fila.get("id_inscripcion"),
            "id_taller": fila.get("id_taller"),
            "nombre": fila.get("taller_nombre") or fila.get("nombre"),
            "id_tipo_taller": fila.get("id_tipo_taller"),
            "categoria": fila.get("tipo_taller") or "",
            "fecha_inicio": ClienteDAO._fecha_iso(fila.get("fecha_inicio")),
            "fecha_fin": ClienteDAO._fecha_iso(fila.get("fecha_fin")),
            "id_estado_taller": fila.get("id_estado_taller"),
            "estado_taller": fila.get("estado_taller") or "",
            "id_estado_inscripcion": fila.get("id_estado_inscripcion"),
            "estado": fila.get("estado_inscripcion") or fila.get("estado_taller") or "",
            "fecha_inscripcion": ClienteDAO._fecha_iso(fila.get("fecha_inscripcion")),
            "coach": fila.get("coach") or ""
        }

    @staticmethod
    def _es_taller_en_curso(taller):
        estado = (taller.get("estado") or "").lower()
        return bool(estado) and not any(
            palabra in estado
            for palabra in ("finalizado", "aprobado", "no aprobado", "rechazado")
        )

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT cedula, nombres, apellidos, correo, telefono, sexo, edad, id_estado
                FROM clientes
            """)
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        clientes = []
        for fila in resultados:
            cliente = ClienteDTO(*fila)
            clientes.append(cliente)

        return clientes

    @staticmethod
    def obtener_por_cedula(cedula):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT cedula, nombres, apellidos, correo, telefono, sexo, edad, id_estado
                FROM clientes
                WHERE cedula = %s
            """, (cedula,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return ClienteDTO(*fila)
        return None

    @staticmethod
    def obtener_panel_cliente(cedula):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT c.cedula, c.nombres, c.apellidos, c.correo, c.telefono,
                       c.sexo, c.edad, c.id_estado, e.nombre AS estado
                FROM clientes c
                LEFT JOIN estados e ON e.id_estado = c.id_estado
                WHERE c.cedula = %s
            """, (cedula,))
            perfil = cursor.fetchone()

            if not perfil:
                return None

            cursor.execute("""
                SELECT pc.id_progreso, pc.cliente_cedula, pc.id_tipo_taller,
                       tt.nombre AS tipo_taller
                FROM progreso_cliente pc
                LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = pc.id_tipo_taller
                WHERE pc.cliente_cedula = %s
            """, (cedula,))
            progreso = cursor.fetchone()

            coaches_sql = """
                SELECT tp.id_taller,
                       GROUP_CONCAT(
                           NULLIF(TRIM(CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, ''))), '')
                           SEPARATOR ', '
                       ) AS coach
                FROM taller_personal tp
                INNER JOIN personal p ON p.cedula = tp.cedula_personal
                INNER JOIN roles r ON r.id_rol = tp.id_rol
                WHERE LOWER(r.nombre) = 'coach'
                GROUP BY tp.id_taller
            """

            cursor.execute(f"""
                SELECT i.id_inscripcion, i.cliente_cedula, i.id_taller,
                       i.id_estado AS id_estado_inscripcion,
                       ei.nombre AS estado_inscripcion,
                       i.fecha_inscripcion,
                       t.nombre AS taller_nombre, t.id_tipo_taller,
                       tt.nombre AS tipo_taller,
                       t.fecha_inicio, t.fecha_fin,
                       t.id_estado AS id_estado_taller,
                       et.nombre AS estado_taller,
                       coaches.coach
                FROM inscripcion i
                INNER JOIN taller t ON t.id_taller = i.id_taller
                LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
                LEFT JOIN estados ei ON ei.id_estado = i.id_estado
                LEFT JOIN estados et ON et.id_estado = t.id_estado
                LEFT JOIN ({coaches_sql}) coaches ON coaches.id_taller = t.id_taller
                WHERE i.cliente_cedula = %s
                ORDER BY i.fecha_inscripcion DESC, t.fecha_inicio DESC, t.nombre ASC
            """, (cedula,))
            historial = [
                ClienteDAO._taller_panel_desde_fila(fila)
                for fila in cursor.fetchall()
            ]

            disponibles = []
            if progreso and progreso.get("id_tipo_taller"):
                cursor.execute(f"""
                    SELECT t.id_taller, t.nombre AS taller_nombre, t.id_tipo_taller,
                           tt.nombre AS tipo_taller,
                           t.fecha_inicio, t.fecha_fin,
                           t.id_estado AS id_estado_taller,
                           et.nombre AS estado_taller,
                           coaches.coach
                    FROM taller t
                    LEFT JOIN tipo_taller tt ON tt.id_tipo_taller = t.id_tipo_taller
                    LEFT JOIN estados et ON et.id_estado = t.id_estado
                    LEFT JOIN ({coaches_sql}) coaches ON coaches.id_taller = t.id_taller
                    WHERE t.id_tipo_taller = %s
                      AND (et.nombre IS NULL OR LOWER(et.nombre) <> 'inactivo')
                      AND NOT EXISTS (
                          SELECT 1
                          FROM inscripcion i
                          WHERE i.id_taller = t.id_taller
                            AND i.cliente_cedula = %s
                      )
                    ORDER BY t.fecha_inicio ASC, t.nombre ASC
                """, (progreso.get("id_tipo_taller"), cedula))
                disponibles = [
                    ClienteDAO._taller_panel_desde_fila(fila)
                    for fila in cursor.fetchall()
                ]

            return {
                "perfil": {
                    **perfil,
                    "estado": perfil.get("estado") or ""
                },
                "progreso": progreso,
                "talleres_en_curso": [
                    taller for taller in historial
                    if ClienteDAO._es_taller_en_curso(taller)
                ],
                "historial_inscripciones": historial,
                "talleres_disponibles": disponibles
            }
        finally:
            conexion.close()

    @staticmethod
    def inscribir_en_taller(cedula, id_taller):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            cursor.execute("SELECT cedula FROM clientes WHERE cedula = %s", (cedula,))
            if not cursor.fetchone():
                raise ValueError("Cliente no encontrado")

            cursor.execute("""
                SELECT t.id_taller, t.id_tipo_taller, e.nombre AS estado_taller
                FROM taller t
                LEFT JOIN estados e ON e.id_estado = t.id_estado
                WHERE t.id_taller = %s
            """, (id_taller,))
            taller = cursor.fetchone()
            if not taller:
                raise ValueError("Taller no encontrado")

            if (taller.get("estado_taller") or "").lower() == "inactivo":
                raise ValueError("El taller no está disponible")

            cursor.execute("""
                SELECT id_tipo_taller
                FROM progreso_cliente
                WHERE cliente_cedula = %s
            """, (cedula,))
            progreso = cursor.fetchone()
            if not progreso:
                raise ValueError("El cliente no tiene progreso registrado")

            if progreso.get("id_tipo_taller") != taller.get("id_tipo_taller"):
                raise ValueError("El taller no corresponde al nivel actual del cliente")

            cursor.execute("""
                SELECT id_inscripcion
                FROM inscripcion
                WHERE cliente_cedula = %s AND id_taller = %s
            """, (cedula, id_taller))
            if cursor.fetchone():
                raise ValueError("El cliente ya está inscrito en este taller")

            cursor.execute("""
                SELECT id_estado
                FROM estados
                WHERE LOWER(nombre) = 'iniciado'
                LIMIT 1
            """)
            estado = cursor.fetchone()
            id_estado = estado["id_estado"] if estado else 3

            cursor.execute("""
                INSERT INTO inscripcion (cliente_cedula, id_taller, id_estado, fecha_inscripcion)
                VALUES (%s, %s, %s, CURDATE())
            """, (cedula, id_taller, id_estado))
            conexion.commit()
            return cursor.lastrowid
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_correo(correo):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT cedula, nombres, apellidos, correo, telefono, sexo, edad, id_estado
                FROM clientes
                WHERE correo = %s
            """, (correo,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return ClienteDTO(*fila)
        return None

    @staticmethod
    def crear(cliente_dto, conexion=None):
        cerrar_conexion = conexion is None
        if cerrar_conexion:
            conexion = Db.obtener_conexion()

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO clientes (cedula, nombres, apellidos, correo, telefono, sexo, edad, id_estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente_dto.cedula,
                cliente_dto.nombres,
                cliente_dto.apellidos,
                cliente_dto.correo,
                cliente_dto.telefono,
                cliente_dto.sexo,
                cliente_dto.edad,
                cliente_dto.id_estado
            ))
            if cerrar_conexion:
                conexion.commit()
        finally:
            if cerrar_conexion:
                conexion.close()

    @staticmethod
    def actualizar(cedula, cliente_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE clientes
                SET nombres = %s, apellidos = %s, correo = %s, telefono = %s,
                    sexo = %s, edad = %s, id_estado = %s
                WHERE cedula = %s
            """, (
                cliente_dto.nombres,
                cliente_dto.apellidos,
                cliente_dto.correo,
                cliente_dto.telefono,
                cliente_dto.sexo,
                cliente_dto.edad,
                cliente_dto.id_estado,
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
            cursor.execute("DELETE FROM clientes WHERE cedula = %s", (cedula,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
