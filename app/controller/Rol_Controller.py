from app.services.Rol_Servicio import RolServicio


class RolController:

    @staticmethod
    def obtener_roles():
        return RolServicio.listar_roles()

    @staticmethod
    def obtener_rol(id_rol):
        return RolServicio.obtener_rol(id_rol)

    @staticmethod
    def crear_rol(data):
        return RolServicio.crear_rol(data)

    @staticmethod
    def actualizar_rol(id_rol, data):
        return RolServicio.actualizar_rol(id_rol, data)

    @staticmethod
    def eliminar_rol(id_rol):
        return RolServicio.eliminar_rol(id_rol)
