import mysql.connector
from mysql.connector import Error
from app.config import Config

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            connect_timeout=10
        )
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