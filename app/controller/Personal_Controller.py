from app.services.Personal_Servicio import PersonalServicio


class PersonalController:

    @staticmethod
    def obtener_personal():
        return PersonalServicio.listar_personal()

    @staticmethod
    def obtener_persona(cedula):
        return PersonalServicio.obtener_persona(cedula)

    @staticmethod
    def crear_persona(data):
        PersonalServicio.crear_persona(data)

    @staticmethod
    def actualizar_persona(cedula, data):
        return PersonalServicio.actualizar_persona(cedula, data)

    @staticmethod
    def eliminar_persona(cedula):
        return PersonalServicio.eliminar_persona(cedula)
