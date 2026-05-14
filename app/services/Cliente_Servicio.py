from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dto.Cliente_DTO import ClienteDTO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO
from app.database.Db import Db

class ClienteServicio:

    @staticmethod
    def listar_clientes():
        clientes = ClienteDAO.obtener_todos()
        return [c.to_dict() for c in clientes]

    @staticmethod
    def obtener_cliente(cedula):
        cliente = ClienteDAO.obtener_por_cedula(cedula)
        if cliente:
            return cliente.to_dict()
        return None

    @staticmethod
    def obtener_panel_cliente(cedula):
        return ClienteDAO.obtener_panel_cliente(cedula)

    @staticmethod
    def inscribir_en_taller(cedula, data):
        id_taller = data.get('id_taller')
        if not id_taller:
            raise ValueError("El id_taller es obligatorio")

        return ClienteDAO.inscribir_en_taller(cedula, id_taller)

    @staticmethod
    def crear_cliente(data):
        if ClienteDAO.obtener_por_cedula(data['cedula']):
            raise ValueError("La cedula ya esta registrada")

        if data.get('correo') and ClienteDAO.obtener_por_correo(data.get('correo')):
            raise ValueError("El correo ya esta registrado")

        cliente = ClienteDTO(
            data['cedula'],
            data['nombres'],
            data['apellidos'],
            data.get('correo'),
            data.get('telefono'),
            data.get('sexo'),
            data.get('edad'),
            data.get('id_estado')
        )

        id_tipo_taller = data.get('id_tipo_taller')

        if not id_tipo_taller:
            ClienteDAO.crear(cliente)
            return

        conexion = Db.obtener_conexion()
        try:
            ClienteDAO.crear(cliente, conexion)
            ProgresoClienteDAO.crear(
                ProgresoClienteDTO(None, data['cedula'], id_tipo_taller),
                conexion
            )
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def actualizar_cliente(cedula, data):
        cliente = ClienteDTO(
            cedula,
            data['nombres'],
            data['apellidos'],
            data.get('correo'),
            data.get('telefono'),
            data.get('sexo'),
            data.get('edad'),
            data.get('id_estado')
        )

        return ClienteDAO.actualizar(cedula, cliente)

    @staticmethod
    def eliminar_cliente(cedula):
        return ClienteDAO.eliminar(cedula)
