class InscripcionDTO:

    def __init__(self, id_inscripcion, cliente_cedula, id_taller, id_estado, fecha_inscripcion):
        self.id_inscripcion = id_inscripcion
        self.cliente_cedula = cliente_cedula
        self.id_taller = id_taller
        self.id_estado = id_estado
        self.fecha_inscripcion = fecha_inscripcion

    def to_dict(self):
        return {
            "id_inscripcion": self.id_inscripcion,
            "cliente_cedula": self.cliente_cedula,
            "id_taller": self.id_taller,
            "id_estado": self.id_estado,
            "fecha_inscripcion": self.fecha_inscripcion.isoformat() if self.fecha_inscripcion else None
        }
