from app.models.dao.Estado_DAO import EstadoDAO
from app.models.dto.Estado_DTO import EstadoDTO


class EstadoServicio:

    @staticmethod
    def listar_estados():
        estados = EstadoDAO.obtener_todos()
        return [estado.to_dict() for estado in estados]

    @staticmethod
    def obtener_estado(id_estado):
        estado = EstadoDAO.obtener_por_id(id_estado)
        if estado:
            return estado.to_dict()
        return None

    @staticmethod
    def crear_estado(data):
        estado = EstadoDTO(None, data['nombre'])
        return EstadoDAO.crear(estado)

    @staticmethod
    def actualizar_estado(id_estado, data):
        estado = EstadoDTO(id_estado, data['nombre'])
        return EstadoDAO.actualizar(id_estado, estado)

    @staticmethod
    def eliminar_estado(id_estado):
        return EstadoDAO.eliminar(id_estado)
