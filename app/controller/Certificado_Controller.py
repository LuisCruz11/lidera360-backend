from app.services.Certificado_Servicio import CertificadoServicio


class CertificadoController:

    @staticmethod
    def generar_pdf_cliente(cedula, id_inscripcion):
        return CertificadoServicio.generar_pdf_cliente(cedula, id_inscripcion)

    @staticmethod
    def verificar(codigo):
        return CertificadoServicio.verificar(codigo)
