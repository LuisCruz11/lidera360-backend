from app.models.dao.Taller_DAO import TallerDAO
from app.models.dto.Taller_DTO import TallerDTO


class TallerServicio:

    @staticmethod
    def listar_talleres():
        talleres = TallerDAO.obtener_todos()
        return [taller.to_dict() for taller in talleres]

    @staticmethod
    def obtener_taller(id_taller):
        taller = TallerDAO.obtener_por_id(id_taller)
        if taller:
            return taller.to_dict()
        return None

    @staticmethod
    def crear_taller(data):
        taller = TallerDTO(
            None,
            data['nombre'],
            data.get('id_tipo_taller'),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            data.get('id_estado')
        )
        return TallerDAO.crear(taller)

    @staticmethod
    def actualizar_taller(id_taller, data):
        taller = TallerDTO(
            id_taller,
            data['nombre'],
            data.get('id_tipo_taller'),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            data.get('id_estado')
        )
        return TallerDAO.actualizar(id_taller, taller)

    @staticmethod
    def eliminar_taller(id_taller):
        return TallerDAO.eliminar(id_taller)
