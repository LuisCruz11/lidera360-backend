class ClienteDTO:

    def __init__(self, cedula, nombres, apellidos, correo, telefono, sexo, edad, id_estado):
        self.cedula = cedula
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.telefono = telefono
        self.sexo = sexo
        self.edad = edad
        self.id_estado = id_estado

    def to_dict(self):
        return {
            "cedula": self.cedula,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "telefono": self.telefono,
            "sexo": self.sexo,
            "edad": self.edad,
            "id_estado": self.id_estado
        }
