class EstadoDTO:

    def __init__(self, id_estado, nombre):
        self.id_estado = id_estado
        self.nombre = nombre

    def to_dict(self):
        return {
            "id_estado": self.id_estado,
            "nombre": self.nombre
        }
