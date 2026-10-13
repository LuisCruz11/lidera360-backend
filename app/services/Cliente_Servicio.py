from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dto.Cliente_DTO import ClienteDTO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO
from app.models.dao.Usuario_DAO import UsuarioDAO
from app.models.dto.Usuario_DTO import UsuarioDTO
from app.database.Db import Db
from app.utils.validaciones import (
    validar_cedula,
    validar_correo,
    validar_edad,
    validar_nombre,
    validar_password,
    validar_telefono,
)
from app.services.Notificacion_Servicio import NotificacionServicio
import bcrypt
from app.services.Estado_Servicio import EstadoServicio

ID_ROL_CLIENTE = 4

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

        id_inscripcion = ClienteDAO.inscribir_en_taller(cedula, id_taller)
        NotificacionServicio.inscripcion_creada(id_inscripcion)
        return id_inscripcion

    @staticmethod
    def cancelar_inscripcion(cedula, id_inscripcion, id_usuario):
        datos_notificacion = NotificacionServicio.datos_para_cancelacion(id_inscripcion)
        ClienteDAO.cancelar_inscripcion(cedula, id_inscripcion, id_usuario)
        NotificacionServicio.inscripcion_cancelada(datos_notificacion)

    @staticmethod
    def actualizar_contacto(cedula, data):
        correo = (data.get('correo') or '').strip()
        telefono = str(data.get('telefono') or '').strip()
        validar_correo(correo, obligatorio=True)
        validar_telefono(telefono, obligatorio=True)

        if not ClienteDAO.obtener_por_cedula(cedula):
            raise LookupError("Cliente no encontrado")

        existente = ClienteDAO.obtener_por_correo(correo)
        if existente and str(existente.cedula) != str(cedula):
            raise ValueError("El correo ya esta registrado")

        ClienteDAO.actualizar_contacto(cedula, correo, telefono)

    @staticmethod
    def crear_cliente(data):
        validar_cedula(data['cedula'])
        validar_nombre(data['nombres'], "El nombre")
        validar_nombre(data['apellidos'], "El apellido")
        validar_telefono(data.get('telefono'))
        validar_correo(data.get('correo'))
        validar_edad(data.get('edad'))
        EstadoServicio.validar_estado_para(data.get('id_estado'), 'cliente')

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise ValueError("Username y password son obligatorios para crear el cliente")

        validar_password(password)

        if ClienteDAO.obtener_por_cedula(data['cedula']):
            raise ValueError("La cedula ya esta registrada")

        if data.get('correo') and ClienteDAO.obtener_por_correo(data.get('correo')):
            raise ValueError("El correo ya esta registrado")

        if UsuarioDAO.obtener_por_username(username):
            raise ValueError("El usuario ya esta registrado")

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

        password_cifrado = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        usuario = UsuarioDTO(
            None,
            username,
            password_cifrado.decode('utf-8'),
            ID_ROL_CLIENTE,
            None,
            True,
            data['cedula']
        )

        id_tipo_taller = data.get('id_tipo_taller')

        conexion = Db.obtener_conexion()
        try:
            ClienteDAO.crear(cliente, conexion)
            UsuarioDAO.crear(usuario, conexion)
            if id_tipo_taller:
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
        validar_nombre(data['nombres'], "El nombre")
        validar_nombre(data['apellidos'], "El apellido")
        validar_telefono(data.get('telefono'))
        validar_correo(data.get('correo'))
        validar_edad(data.get('edad'))
        EstadoServicio.validar_estado_para(data.get('id_estado'), 'cliente')

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

        id_tipo_taller = data.get('id_tipo_taller')

        if not id_tipo_taller:
            return ClienteDAO.actualizar(cedula, cliente)

        conexion = Db.obtener_conexion()
        try:
            actualizado = ClienteDAO.actualizar(cedula, cliente, conexion)

            progreso_existente = ProgresoClienteDAO.obtener_por_cliente(cedula)
            if progreso_existente:
                ProgresoClienteDAO.actualizar(
                    progreso_existente.id_progreso,
                    ProgresoClienteDTO(progreso_existente.id_progreso, cedula, id_tipo_taller),
                    conexion
                )
            else:
                ProgresoClienteDAO.crear(ProgresoClienteDTO(None, cedula, id_tipo_taller), conexion)

            conexion.commit()
            return actualizado
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def eliminar_cliente(cedula):
        return ClienteDAO.eliminar(cedula)
