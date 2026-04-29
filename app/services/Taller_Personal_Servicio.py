from app.models.dao.Taller_Personal_DAO import TallerPersonalDAO
from app.models.dto.Taller_Personal_DTO import TallerPersonalDTO


class TallerPersonalServicio:

    @staticmethod
    def listar_taller_personal():
        registros = TallerPersonalDAO.obtener_todos()
        return [registro.to_dict() for registro in registros]

    @staticmethod
    def obtener_taller_personal(id_taller_personal):
        registro = TallerPersonalDAO.obtener_por_id(id_taller_personal)
        if registro:
            return registro.to_dict()
        return None

    @staticmethod
    def crear_taller_personal(data):
        registro = TallerPersonalDTO(
            None,
            data.get('id_taller'),
            data.get('cedula_personal'),
            data.get('rol_en_taller')
        )
        return TallerPersonalDAO.crear(registro)

    @staticmethod
    def actualizar_taller_personal(id_taller_personal, data):
        registro = TallerPersonalDTO(
            id_taller_personal,
            data.get('id_taller'),
            data.get('cedula_personal'),
            data.get('rol_en_taller')
        )
        return TallerPersonalDAO.actualizar(id_taller_personal, registro)

    @staticmethod
    def eliminar_taller_personal(id_taller_personal):
        return TallerPersonalDAO.eliminar(id_taller_personal)
