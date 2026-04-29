class RolDTO:

    def __init__(self, id_rol, nombre):
        self.id_rol = id_rol
        self.nombre = nombre

    def to_dict(self):
        return {
            "id_rol": self.id_rol,
            "nombre": self.nombre
        }
