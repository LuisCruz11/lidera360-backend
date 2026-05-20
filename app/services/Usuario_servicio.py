from app.models.dao.Usuario_DAO import UsuarioDAO
from app.models.dto.Usuario_DTO import UsuarioDTO
from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dto.Cliente_DTO import ClienteDTO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO
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
        usuario_existente = UsuarioDAO.obtener_por_username(data['username'])
        
        if not usuario_existente:
            raise ValueError("No se encontró ningún usuario con ese nombre de usuario.")
        
        usuario = UsuarioDAO.login(data['username'], data['password'])
        
        if usuario:
            return usuario.to_dict()
        
        raise ValueError("Credenciales incorrectas. Verifica tu contraseña.")

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
            ProgresoClienteDAO.crear(ProgresoClienteDTO(None, data['cedula'], 1), conexion)
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        correo_enviado = True
        try:
            enviar_correo_registro(data['correo'], data['nombres'])
        except Exception as error:
            print(f"Error enviando correo de registro: {error}", flush=True)
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

    @staticmethod
    def crear_admin_desde_personal(data):
        # data debe contener: cedula_personal, username, password, opcional: id_rol, activo
        required = ['cedula_personal', 'username', 'password']
        for campo in required:
            if campo not in data or not data[campo]:
                raise ValueError(f"Falta el campo requerido: {campo}")

        cedula = data['cedula_personal']
        username = data['username']
        password = data['password']
        id_rol = data.get('id_rol', 5)  # 5 = Admin según attachments
        activo = data.get('activo', 1)

        if UsuarioDAO.obtener_por_username(username):
            raise ValueError("El username ya está registrado")

        if UsuarioDAO.obtener_por_cedula_personal(cedula):
            raise ValueError("El personal ya tiene un usuario asignado")

        password_cifrado = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        usuario = UsuarioDTO(
            None,
            username,
            password_cifrado.decode('utf-8'),
            id_rol,
            cedula,
            activo,
            None
        )

        conexion = Db.obtener_conexion()
        try:
            id_usuario = UsuarioDAO.crear(usuario, conexion)
            conexion.commit()
            return {"id_usuario": id_usuario}
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
