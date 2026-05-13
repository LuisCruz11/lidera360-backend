from app.services.Cliente_Servicio import ClienteServicio

class ClienteController:

    @staticmethod
    def obtener_clientes():
        return ClienteServicio.listar_clientes()

    @staticmethod
    def obtener_cliente(cedula):
        return ClienteServicio.obtener_cliente(cedula)

    @staticmethod
    def obtener_panel_cliente(cedula):
        return ClienteServicio.obtener_panel_cliente(cedula)

    @staticmethod
    def inscribir_en_taller(cedula, data):
        return ClienteServicio.inscribir_en_taller(cedula, data)

    @staticmethod
    def crear_cliente(data):
        ClienteServicio.crear_cliente(data)

    @staticmethod
    def actualizar_cliente(cedula, data):
        return ClienteServicio.actualizar_cliente(cedula, data)

    @staticmethod
    def eliminar_cliente(cedula):
        return ClienteServicio.eliminar_cliente(cedula)
