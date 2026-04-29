class ProgresoClienteDTO:

    def __init__(self, id_progreso, cliente_cedula, id_tipo_taller):
        self.id_progreso = id_progreso
        self.cliente_cedula = cliente_cedula
        self.id_tipo_taller = id_tipo_taller

    def to_dict(self):
        return {
            "id_progreso": self.id_progreso,
            "cliente_cedula": self.cliente_cedula,
            "id_tipo_taller": self.id_tipo_taller
        }
