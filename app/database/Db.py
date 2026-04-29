import pymysql
from app.Config import Config

class Db:
    @staticmethod
    def obtener_conexion():
        return pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=3306
        )
