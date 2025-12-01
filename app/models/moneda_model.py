import mysql.connector
from app.database import get_db_connection, close_db_connection

class MonedaModel:
    def __init__(self):
        pass

    def get_all_monedas(self):
        """Obtiene todas las monedas."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM moneda ORDER BY nombre"
            cursor.execute(query)
            monedas = cursor.fetchall()
            return monedas
        except mysql.connector.Error as err:
            print(f"Error al obtener monedas: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_moneda(self, nombre, simbolo, codigo_iso):
        """Crea una nueva moneda."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si ya existe el código ISO o nombre
            check_query = """
            SELECT COUNT(*) FROM moneda 
            WHERE codigo_iso = %s OR nombre = %s
            """
            cursor.execute(check_query, (codigo_iso, nombre))
            if cursor.fetchone()[0] > 0:
                return False

            query = """
            INSERT INTO moneda (nombre, simbolo, codigo_iso)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (nombre, simbolo, codigo_iso))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al crear moneda: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_moneda(self, id_moneda):
        """Elimina una moneda."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si la moneda está siendo usada
            check_query = "SELECT COUNT(*) FROM empresa WHERE id_moneda_base = %s"
            cursor.execute(check_query, (id_moneda,))
            if cursor.fetchone()[0] > 0:
                return False

            query = "DELETE FROM moneda WHERE id_moneda = %s"
            cursor.execute(query, (id_moneda,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar moneda: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)