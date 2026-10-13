from app.models.dao.Certificado_DAO import CertificadoDAO
from app.utils.certificado_pdf import generar_certificado_pdf


class CertificadoServicio:

    @staticmethod
    def generar_pdf_cliente(cedula, id_inscripcion):
        certificado = CertificadoDAO.obtener_vigente_de_cliente(cedula, id_inscripcion)
        if not certificado:
            raise LookupError("No hay un certificado disponible para esta inscripción")

        nombre_archivo = f"Certificado-{certificado['taller']}-{certificado['codigo']}.pdf".replace(" ", "_")
        return generar_certificado_pdf(certificado), nombre_archivo

    @staticmethod
    def verificar(codigo):
        certificado = CertificadoDAO.obtener_por_codigo((codigo or "").strip().upper())
        if not certificado:
            return {"valido": False, "mensaje": "No existe un certificado con ese código"}

        return {
            "valido": not certificado["anulado"],
            "mensaje": "Certificado anulado" if certificado["anulado"] else "Certificado válido",
            "codigo": certificado["codigo"],
            "participante": f"{certificado['nombres']} {certificado['apellidos']}".strip(),
            "taller": certificado["taller"],
            "nivel": certificado.get("nivel") or "",
            "fecha_emision": certificado["fecha_emision"].isoformat() if certificado["fecha_emision"] else None,
        }
