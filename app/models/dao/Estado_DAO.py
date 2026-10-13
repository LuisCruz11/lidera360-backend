from app.database.Db import Db
from app.models.dto.Estado_DTO import EstadoDTO


class EstadoDAO:

    @staticmethod
    def obtener_todos(aplica_a=None):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            if aplica_a:
                cursor.execute("""
                    SELECT id_estado, nombre, aplica_a
                    FROM estados
                    WHERE FIND_IN_SET(%s, aplica_a)
                    ORDER BY id_estado
                """, (aplica_a,))
            else:
                cursor.execute("SELECT id_estado, nombre, aplica_a FROM estados ORDER BY id_estado")
            resultados = cursor.fetchall()
        finally:
            conexion.close()

        return [EstadoDTO(*fila) for fila in resultados]

    @staticmethod
    def obtener_por_id(id_estado):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_estado, nombre, aplica_a FROM estados WHERE id_estado = %s", (id_estado,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return EstadoDTO(*fila)
        return None

    @staticmethod
    def crear(estado_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO estados (nombre, aplica_a) VALUES (%s, %s)",
                (estado_dto.nombre, ",".join(estado_dto.aplica_a))
            )
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_estado, estado_dto):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE estados SET nombre = %s, aplica_a = %s WHERE id_estado = %s",
                (estado_dto.nombre, ",".join(estado_dto.aplica_a), id_estado)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_estado):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM estados WHERE id_estado = %s", (id_estado,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()
