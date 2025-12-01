import mysql.connector
from app.database import get_db_connection, close_db_connection

class TipoMovimientoModel:
    def __init__(self):
        pass

    def get_all_tipos_movimiento(self):
        """Obtiene todos los tipos de movimiento."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM tipo_movimiento ORDER BY nombre"
            cursor.execute(query)
            tipos = cursor.fetchall()
            return tipos
        except mysql.connector.Error as err:
            print(f"Error al obtener tipos de movimiento: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_tipo_movimiento_by_id(self, id_tipo_movimiento):
        """Obtiene un tipo de movimiento por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM tipo_movimiento WHERE id_tipo_movimiento = %s"
            cursor.execute(query, (id_tipo_movimiento,))
            tipo = cursor.fetchone()
            return tipo
        except mysql.connector.Error as err:
            print(f"Error al obtener tipo de movimiento: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_tipos_entrada(self):
        """Obtiene solo los tipos de movimiento de entrada."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM tipo_movimiento WHERE es_entrada = 1 ORDER BY nombre"
            cursor.execute(query)
            tipos = cursor.fetchall()
            return tipos
        except mysql.connector.Error as err:
            print(f"Error al obtener tipos de entrada: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_tipos_salida(self):
        """Obtiene solo los tipos de movimiento de salida."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM tipo_movimiento WHERE es_entrada = 0 ORDER BY nombre"
            cursor.execute(query)
            tipos = cursor.fetchall()
            return tipos
        except mysql.connector.Error as err:
            print(f"Error al obtener tipos de salida: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)