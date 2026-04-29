from app.models.dao.Usuario_DAO import UsuarioDAO
from app.models.dto.Usuario_DTO import UsuarioDTO

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
    def crear_usuario(data):
        usuario = UsuarioDTO(
            None,
            data['username'],
            data['password'],
            data.get('id_rol'),
            data.get('cedula_personal'),
            data.get('activo', True)
        )
        return UsuarioDAO.crear(usuario)

    @staticmethod
    def actualizar_usuario(id_usuario, data):
        usuario = UsuarioDTO(
            id_usuario,
            data['username'],
            data['password'],
            data.get('id_rol'),
            data.get('cedula_personal'),
            data.get('activo', True)
        )
        return UsuarioDAO.actualizar(id_usuario, usuario)

    @staticmethod
    def eliminar_usuario(id_usuario):
        return UsuarioDAO.eliminar(id_usuario)
