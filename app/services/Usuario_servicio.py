from app.models.dao.Usuario_DAO import UsuarioDAO
from app.models.dto.Usuario_DTO import UsuarioDTO
from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dto.Cliente_DTO import ClienteDTO
from app.utils.email_service import enviar_correo_registro
from app.database.Db import Db
import bcrypt

class UsuarioServicio:

    @staticmethod
    def listar_usuarios():
        usuarios = UsuarioDAO.obtener_todos()
        return [usuario.to_dict() for usuario in usuarios]

    @staticmethod
    def obtener_usuario(id_usuario):
        usuario = UsuarioDAO.obtener_por_id(id_usuario)
        if usuario:
            return usuario.to_dict()
        return None

    @staticmethod
    def login(data):
        usuario = UsuarioDAO.login(data['username'], data['password'])

        if usuario:
            return usuario.to_dict()

        return None

    @staticmethod
    def registrar_cliente_usuario(data):

        if ClienteDAO.obtener_por_cedula(data['cedula']):
            raise ValueError("La cedula ya esta registrada")

        if ClienteDAO.obtener_por_correo(data['correo']):
            raise ValueError("El correo ya esta registrado")

        if UsuarioDAO.obtener_por_username(data['username']):
            raise ValueError("El usuario ya esta registrado")

        cliente = ClienteDTO(
            data['cedula'],
            data['nombres'],
            data['apellidos'],
            data['correo'],
            data['telefono'],
            data['sexo'],
            data['edad'],
            1
        )

        password_cifrado = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        )

        usuario = UsuarioDTO(
            None,
            data['username'],
            password_cifrado.decode('utf-8'),
            4,
            None,
            1,
            data['cedula']
        )

        conexion = Db.obtener_conexion()
        try:
            ClienteDAO.crear(cliente, conexion)
            UsuarioDAO.crear(usuario, conexion)
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        correo_enviado = True
        try:
            enviar_correo_registro(data['correo'], data['nombres'])
        except Exception:
            correo_enviado = False

        return correo_enviado

    @staticmethod
    def actualizar_usuario(id_usuario, data):
        usuario = UsuarioDTO(
            id_usuario,
            data['username'],
            data['password'],
            data.get('id_rol'),
            data.get('cedula_personal'),
            data.get('activo', True),
            data.get('cedula_cliente')
        )
        return UsuarioDAO.actualizar(id_usuario, usuario)

    @staticmethod
    def eliminar_usuario(id_usuario):
        return UsuarioDAO.eliminar(id_usuario)
