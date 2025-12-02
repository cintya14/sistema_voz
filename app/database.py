# app/database.py
import pymysql
from pymysql import Error
from app.config import Config

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,  # ✅ AGREGAR ESTO
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10  # ✅ AGREGAR TIMEOUT
        )
        print("Conexión a la base de datos MySQL exitosa.")
        return connection
    except Error as e:
        print(f"Error al conectar a la base de datos MySQL: {e}")
        return None

def close_db_connection(connection):
    """Cierra la conexión a la base de datos."""
    if connection and connection.open:
        connection.close()
        print("Conexión a la base de datos MySQL cerrada.")

# Ejemplo de uso (solo para prueba, no se usará directamente en el flujo MVC)
if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT VERSION();")
            db_version = cursor.fetchone()
            print(f"Versión de la base de datos MySQL: {db_version}")
        except Error as e:
            print(f"Error al ejecutar consulta: {e}")
        finally:
            cursor.close()
            close_db_connection(conn)