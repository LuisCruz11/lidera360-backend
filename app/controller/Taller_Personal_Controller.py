from app.services.Taller_Personal_Servicio import TallerPersonalServicio


class TallerPersonalController:

    @staticmethod
    def obtener_taller_personal_lista():
        return TallerPersonalServicio.listar_taller_personal()

    @staticmethod
    def obtener_taller_personal(id_taller_personal):
        return TallerPersonalServicio.obtener_taller_personal(id_taller_personal)

    @staticmethod
    def crear_taller_personal(data):
        return TallerPersonalServicio.crear_taller_personal(data)

    @staticmethod
    def actualizar_taller_personal(id_taller_personal, data):
        return TallerPersonalServicio.actualizar_taller_personal(id_taller_personal, data)

    @staticmethod
    def eliminar_taller_personal(id_taller_personal):
        return TallerPersonalServicio.eliminar_taller_personal(id_taller_personal)
