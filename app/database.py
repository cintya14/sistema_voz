# app/database.py
import mysql.connector
from mysql.connector import Error
from app.config import Config

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        if connection.is_connected():
            print("Conexión a la base de datos MySQL exitosa.")
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos MySQL: {e}")
        return None

def close_db_connection(connection):
    """Cierra la conexión a la base de datos."""
    if connection and connection.is_connected():
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
            print(f"Versión de la base de datos MySQL: {db_version[0]}")
        except Error as e:
            print(f"Error al ejecutar consulta: {e}")
        finally:
            cursor.close()
            close_db_connection(conn)