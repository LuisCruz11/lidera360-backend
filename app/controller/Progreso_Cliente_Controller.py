from app.services.Progreso_Cliente_Servicio import ProgresoClienteServicio


class ProgresoClienteController:

    @staticmethod
    def obtener_progresos():
        return ProgresoClienteServicio.listar_progresos()

    @staticmethod
    def obtener_progreso(id_progreso):
        return ProgresoClienteServicio.obtener_progreso(id_progreso)

    @staticmethod
    def crear_progreso(data):
        return ProgresoClienteServicio.crear_progreso(data)

    @staticmethod
    def actualizar_progreso(id_progreso, data):
        return ProgresoClienteServicio.actualizar_progreso(id_progreso, data)

    @staticmethod
    def eliminar_progreso(id_progreso):
        return ProgresoClienteServicio.eliminar_progreso(id_progreso)
