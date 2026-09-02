from app.services.Taller_Servicio import TallerServicio


class TallerController:

    @staticmethod
    def obtener_talleres():
        return TallerServicio.listar_talleres()

    @staticmethod
    def obtener_taller(id_taller):
        return TallerServicio.obtener_taller(id_taller)

    @staticmethod
    def obtener_detalle(id_taller):
        return TallerServicio.obtener_detalle(id_taller)

    @staticmethod
    def agregar_nota(id_taller, id_usuario, data):
        return TallerServicio.agregar_nota(id_taller, id_usuario, data)

    @staticmethod
    def crear_taller(data):
        return TallerServicio.crear_taller(data)

    @staticmethod
    def actualizar_taller(id_taller, data):
        return TallerServicio.actualizar_taller(id_taller, data)

    @staticmethod
    def eliminar_taller(id_taller):
        return TallerServicio.eliminar_taller(id_taller)
