import os

from fpdf import FPDF

RUTA_LOGO = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'logo.png')

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

MORADO_OSCURO = (43, 18, 63)
MORADO = (122, 60, 224)
LILA = (130, 99, 159)


def _fecha_larga(fecha):
    if not fecha:
        return ""
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def _texto_centrado(pdf, texto, tamano, color=MORADO_OSCURO, estilo="", alto=10):
    pdf.set_font("Helvetica", estilo, tamano)
    pdf.set_text_color(*color)
    pdf.cell(0, alto, texto, align="C", new_x="LMARGIN", new_y="NEXT")


def generar_certificado_pdf(certificado):
    """Genera el PDF del certificado y devuelve sus bytes.
    `certificado` es la fila de CertificadoDAO (nombres, taller, nivel, fechas, coach, código...)."""
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.set_margins(25, 20, 25)
    pdf.add_page()

    ancho, alto = pdf.w, pdf.h

    pdf.set_draw_color(*MORADO)
    pdf.set_line_width(2)
    pdf.rect(8, 8, ancho - 16, alto - 16)
    pdf.set_line_width(0.4)
    pdf.rect(12, 12, ancho - 24, alto - 24)

    if os.path.exists(RUTA_LOGO):
        pdf.image(RUTA_LOGO, x=(ancho - 26) / 2, y=18, w=26)

    pdf.set_y(48)
    _texto_centrado(pdf, "LIDERA360", 12, MORADO, "B", 6)
    pdf.ln(2)
    _texto_centrado(pdf, "CERTIFICADO DE APROBACIÓN", 26, MORADO_OSCURO, "B", 14)
    pdf.ln(6)
    _texto_centrado(pdf, "Se certifica que", 13, LILA, "", 8)

    nombre = f"{certificado['nombres']} {certificado['apellidos']}".strip()
    _texto_centrado(pdf, nombre, 28, MORADO_OSCURO, "B", 16)
    _texto_centrado(pdf, f"identificado(a) con cédula N.º {certificado['cliente_cedula']}", 12, LILA, "", 8)
    pdf.ln(4)
    _texto_centrado(pdf, "aprobó satisfactoriamente el taller", 13, LILA, "", 8)
    _texto_centrado(pdf, certificado["taller"], 20, MORADO, "B", 12)

    detalle = f"Nivel {certificado['nivel']}" if certificado.get("nivel") else ""
    if certificado.get("fecha_inicio") and certificado.get("fecha_fin"):
        periodo = f"realizado del {_fecha_larga(certificado['fecha_inicio'])} al {_fecha_larga(certificado['fecha_fin'])}"
        detalle = f"{detalle} · {periodo}" if detalle else periodo
    if detalle:
        _texto_centrado(pdf, detalle, 12, LILA, "", 8)

    y_firma = alto - 52
    if certificado.get("coach"):
        pdf.set_draw_color(*LILA)
        pdf.line(ancho / 2 - 45, y_firma, ancho / 2 + 45, y_firma)
        pdf.set_y(y_firma + 2)
        _texto_centrado(pdf, certificado["coach"], 12, MORADO_OSCURO, "B", 6)
        _texto_centrado(pdf, "Coach del taller", 10, LILA, "", 6)

    pdf.set_y(alto - 30)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*LILA)
    pdf.cell(0, 5, f"Emitido el {_fecha_larga(certificado['fecha_emision'])}", align="L")
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 5, f"Código de verificación: {certificado['codigo']}", align="R")

    return bytes(pdf.output())
