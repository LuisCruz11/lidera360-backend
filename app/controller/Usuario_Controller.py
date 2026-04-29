from app.services.Usuario_servicio import UsuarioServicio

class UsuarioController:

    @staticmethod
    def obtener_usuarios():
        return UsuarioServicio.listar_usuarios()

    @staticmethod
    def obtener_usuario(id_usuario):
        return UsuarioServicio.obtener_usuario(id_usuario)

    @staticmethod
    def login(data):
        return UsuarioServicio.login(data)

    @staticmethod
    def crear_usuario(data):
        return UsuarioServicio.crear_usuario(data)

    @staticmethod
    def actualizar_usuario(id_usuario, data):
        return UsuarioServicio.actualizar_usuario(id_usuario, data)

    @staticmethod
    def eliminar_usuario(id_usuario):
        return UsuarioServicio.eliminar_usuario(id_usuario)
