from app.database.Db import Db
from app.models.dto.Cliente_DTO import ClienteDTO


class ClienteDAO:

    @staticmethod
    def obtener_todos():
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM clientes")
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
            cursor.execute("SELECT * FROM clientes WHERE cedula = %s", (cedula,))
            fila = cursor.fetchone()
        finally:
            conexion.close()

        if fila:
            return ClienteDTO(*fila)
        return None

    @staticmethod
    def obtener_por_correo(correo):
        conexion = Db.obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM clientes WHERE correo = %s", (correo,))
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
