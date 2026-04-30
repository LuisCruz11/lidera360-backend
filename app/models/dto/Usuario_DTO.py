class UsuarioDTO:

    def __init__(self, id_usuario, username, password, id_rol, cedula_personal, activo, cedula_cliente=None):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
        self.id_rol = id_rol
        self.cedula_personal = cedula_personal
        self.activo = activo
        self.cedula_cliente = cedula_cliente

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "id_rol": self.id_rol,
            "cedula_personal": self.cedula_personal,
            "cedula_cliente": self.cedula_cliente,
            "activo": bool(self.activo)
        }
