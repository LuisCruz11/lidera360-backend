class TallerPersonalDTO:

    def __init__(self, id_taller_personal, id_taller, cedula_personal, rol_en_taller):
        self.id_taller_personal = id_taller_personal
        self.id_taller = id_taller
        self.cedula_personal = cedula_personal
        self.rol_en_taller = rol_en_taller

    def to_dict(self):
        return {
            "id_taller_personal": self.id_taller_personal,
            "id_taller": self.id_taller,
            "cedula_personal": self.cedula_personal,
            "rol_en_taller": self.rol_en_taller
        }
