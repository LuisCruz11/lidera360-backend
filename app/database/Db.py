import pymysql
from pymysql.constants import CLIENT
from app.Config import Config

class Db:
    @staticmethod
    def obtener_conexion():
        return pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=3306,
            # Que rowcount de un UPDATE cuente las filas encontradas y no solo las modificadas:
            # guardar un registro sin cambios no debe tomarse como "no encontrado".
            client_flag=CLIENT.FOUND_ROWS
        )
