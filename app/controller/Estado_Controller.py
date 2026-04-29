from app.services.Estado_Servicio import EstadoServicio


class EstadoController:

    @staticmethod
    def obtener_estados():
        return EstadoServicio.listar_estados()

    @staticmethod
    def obtener_estado(id_estado):
        return EstadoServicio.obtener_estado(id_estado)

    @staticmethod
    def crear_estado(data):
        return EstadoServicio.crear_estado(data)

    @staticmethod
    def actualizar_estado(id_estado, data):
        return EstadoServicio.actualizar_estado(id_estado, data)

    @staticmethod
    def eliminar_estado(id_estado):
        return EstadoServicio.eliminar_estado(id_estado)
