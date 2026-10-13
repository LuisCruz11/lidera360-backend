from app.services.Reporte_Servicio import ReporteServicio


class ReporteController:

    @staticmethod
    def generar(tipo, parametros):
        return ReporteServicio.generar(tipo, parametros)
