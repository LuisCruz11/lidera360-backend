from app.models.dao.Tipo_Taller_DAO import TipoTallerDAO
from app.models.dto.Tipo_Taller_DTO import TipoTallerDTO


class TipoTallerServicio:

    @staticmethod
    def listar_tipos_taller():
        tipos = TipoTallerDAO.obtener_todos()
        return [tipo.to_dict() for tipo in tipos]

    @staticmethod
    def obtener_tipo_taller(id_tipo_taller):
        tipo = TipoTallerDAO.obtener_por_id(id_tipo_taller)
        if tipo:
            return tipo.to_dict()
        return None

    @staticmethod
    def crear_tipo_taller(data):
        tipo = TipoTallerDTO(None, data['nombre'])
        return TipoTallerDAO.crear(tipo)

    @staticmethod
    def actualizar_tipo_taller(id_tipo_taller, data):
        tipo = TipoTallerDTO(id_tipo_taller, data['nombre'])
        return TipoTallerDAO.actualizar(id_tipo_taller, tipo)

    @staticmethod
    def eliminar_tipo_taller(id_tipo_taller):
        return TipoTallerDAO.eliminar(id_tipo_taller)
