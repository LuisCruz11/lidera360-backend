from app.models.dao.Rol_DAO import RolDAO
from app.models.dto.Rol_DTO import RolDTO


class RolServicio:

    @staticmethod
    def listar_roles():
        roles = RolDAO.obtener_todos()
        return [rol.to_dict() for rol in roles]

    @staticmethod
    def obtener_rol(id_rol):
        rol = RolDAO.obtener_por_id(id_rol)
        if rol:
            return rol.to_dict()
        return None

    @staticmethod
    def crear_rol(data):
        rol = RolDTO(None, data['nombre'])
        return RolDAO.crear(rol)

    @staticmethod
    def actualizar_rol(id_rol, data):
        rol = RolDTO(id_rol, data['nombre'])
        return RolDAO.actualizar(id_rol, rol)

    @staticmethod
    def eliminar_rol(id_rol):
        return RolDAO.eliminar(id_rol)
