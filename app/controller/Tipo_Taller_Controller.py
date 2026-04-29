from app.services.Tipo_Taller_Servicio import TipoTallerServicio


class TipoTallerController:

    @staticmethod
    def obtener_tipos_taller():
        return TipoTallerServicio.listar_tipos_taller()

    @staticmethod
    def obtener_tipo_taller(id_tipo_taller):
        return TipoTallerServicio.obtener_tipo_taller(id_tipo_taller)

    @staticmethod
    def crear_tipo_taller(data):
        return TipoTallerServicio.crear_tipo_taller(data)

    @staticmethod
    def actualizar_tipo_taller(id_tipo_taller, data):
        return TipoTallerServicio.actualizar_tipo_taller(id_tipo_taller, data)

    @staticmethod
    def eliminar_tipo_taller(id_tipo_taller):
        return TipoTallerServicio.eliminar_tipo_taller(id_tipo_taller)
