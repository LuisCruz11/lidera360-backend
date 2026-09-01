from app.models.dao.Usuario_DAO import UsuarioDAO
from app.models.dto.Usuario_DTO import UsuarioDTO
from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dto.Cliente_DTO import ClienteDTO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO
from app.utils.email_service import enviar_correo_registro
from app.database.Db import Db
from app.utils.validaciones import (
    validar_cedula,
    validar_correo,
    validar_nombre,
    validar_password,
    validar_telefono,
)
from flask_jwt_extended import create_access_token
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
            token = create_access_token(
                identity=str(usuario.id_usuario),
                additional_claims={"id_rol": usuario.id_rol, "username": usuario.username}
            )
            return {"token": token, "usuario": usuario.to_dict()}

        raise ValueError("Credenciales incorrectas. Verifica tu contraseña.")

    @staticmethod
    def registrar_cliente_usuario(data):
        validar_cedula(data['cedula'])
        validar_nombre(data['nombres'], "El nombre")
        validar_nombre(data['apellidos'], "El apellido")
        validar_telefono(data['telefono'], obligatorio=True)
        validar_correo(data['correo'], obligatorio=True)
        validar_password(data['password'])

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
    def cambiar_password(id_usuario, data):
        password_actual = data.get('password_actual')
        password_nueva = data.get('password_nueva')

        if not password_actual or not password_nueva:
            raise ValueError("La contraseña actual y la nueva son obligatorias")

        validar_password(password_nueva)

        usuario = UsuarioDAO.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if not bcrypt.checkpw(password_actual.encode('utf-8'), usuario.password.encode('utf-8')):
            raise ValueError("La contraseña actual no es correcta")

        password_cifrado = bcrypt.hashpw(
            password_nueva.encode('utf-8'),
            bcrypt.gensalt()
        )
        UsuarioDAO.actualizar_password(id_usuario, password_cifrado.decode('utf-8'))

    @staticmethod
    def actualizar_usuario(id_usuario, data):
        usuario_actual = UsuarioDAO.obtener_por_id(id_usuario)
        if not usuario_actual:
            return False

        usuario = UsuarioDTO(
            id_usuario,
            data.get('username', usuario_actual.username),
            usuario_actual.password,
            data.get('id_rol', usuario_actual.id_rol),
            data.get('cedula_personal', usuario_actual.cedula_personal),
            data.get('activo', usuario_actual.activo),
            data.get('cedula_cliente', usuario_actual.cedula_cliente)
        )
        return UsuarioDAO.actualizar(id_usuario, usuario)

    @staticmethod
    def eliminar_usuario(id_usuario):
        return UsuarioDAO.eliminar(id_usuario)
