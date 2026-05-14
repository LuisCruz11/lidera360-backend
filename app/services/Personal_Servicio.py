from app.models.dao.Personal_DAO import PersonalDAO
from app.models.dto.Personal_DTO import PersonalDTO
from app.models.dao.Usuario_DAO import UsuarioDAO
from app.models.dto.Usuario_DTO import UsuarioDTO
from app.database.Db import Db
import bcrypt


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
        if PersonalDAO.obtener_por_cedula(data['cedula']):
            raise ValueError("La cedula ya esta registrada en personal")

        persona = PersonalDTO(
            data['cedula'],
            data.get('nombres'),
            data.get('apellidos'),
            data.get('correo'),
            data.get('telefono'),
            data.get('id_rol')
        )

        username = data.get('username')
        password = data.get('password')

        if not username and not password:
            PersonalDAO.crear(persona)
            return {"cedula": persona.cedula}

        if not username or not password:
            raise ValueError("Username y password son obligatorios para crear el usuario")

        if UsuarioDAO.obtener_por_username(username):
            raise ValueError("El usuario ya esta registrado")

        if UsuarioDAO.obtener_por_cedula_personal(data['cedula']):
            raise ValueError("El personal ya tiene un usuario asignado")

        password_cifrado = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        usuario = UsuarioDTO(
            None,
            username,
            password_cifrado.decode('utf-8'),
            data.get('id_rol'),
            data['cedula'],
            data.get('activo', True),
            None
        )

        conexion = Db.obtener_conexion()
        try:
            PersonalDAO.crear(persona, conexion)
            id_usuario = UsuarioDAO.crear(usuario, conexion)
            conexion.commit()
            return {"cedula": persona.cedula, "id_usuario": id_usuario}
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

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
