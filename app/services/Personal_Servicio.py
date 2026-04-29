from app.models.dao.Personal_DAO import PersonalDAO
from app.models.dto.Personal_DTO import PersonalDTO


class PersonalServicio:

    @staticmethod
    def listar_personal():
        personal = PersonalDAO.obtener_todos()
        return [persona.to_dict() for persona in personal]

    @staticmethod
    def obtener_persona(cedula):
        persona = PersonalDAO.obtener_por_cedula(cedula)
        if persona:
            return persona.to_dict()
        return None

    @staticmethod
    def crear_persona(data):
        persona = PersonalDTO(
            data['cedula'],
            data.get('nombres'),
            data.get('apellidos'),
            data.get('correo'),
            data.get('telefono'),
            data.get('id_rol')
        )
        PersonalDAO.crear(persona)

    @staticmethod
    def actualizar_persona(cedula, data):
        persona = PersonalDTO(
            cedula,
            data.get('nombres'),
            data.get('apellidos'),
            data.get('correo'),
            data.get('telefono'),
            data.get('id_rol')
        )
        return PersonalDAO.actualizar(cedula, persona)

    @staticmethod
    def eliminar_persona(cedula):
        return PersonalDAO.eliminar(cedula)
