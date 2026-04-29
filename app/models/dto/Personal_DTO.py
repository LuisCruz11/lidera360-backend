class PersonalDTO:

    def __init__(self, cedula, nombres, apellidos, correo, telefono, id_rol):
        self.cedula = cedula
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.telefono = telefono
        self.id_rol = id_rol

    def to_dict(self):
        return {
            "cedula": self.cedula,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "telefono": self.telefono,
            "id_rol": self.id_rol
        }
