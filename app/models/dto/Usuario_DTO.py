class UsuarioDTO:

    def __init__(self, id_usuario, username, password, id_rol, cedula_personal, activo):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
        self.id_rol = id_rol
        self.cedula_personal = cedula_personal
        self.activo = activo

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "id_rol": self.id_rol,
            "cedula_personal": self.cedula_personal,
            "activo": bool(self.activo)
        }
