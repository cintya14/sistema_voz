import mysql.connector
from datetime import datetime
from app.database import get_db_connection, close_db_connection

class IgvModel:
    def __init__(self):
        pass

    def get_all_igv(self):
        """Obtiene todas las tasas de IGV ordenadas por fecha."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT * FROM igv 
            ORDER BY fecha_inicio DESC
            """
            cursor.execute(query)
            tasas = cursor.fetchall()
            return tasas
        except mysql.connector.Error as err:
            print(f"Error al obtener tasas de IGV: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_igv_actual(self):
        """Obtiene la tasa de IGV vigente (más reciente)."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT * FROM igv 
            WHERE fecha_inicio <= CURDATE()
            ORDER BY fecha_inicio DESC 
            LIMIT 1
            """
            cursor.execute(query)
            tasa = cursor.fetchone()
            return tasa
        except mysql.connector.Error as err:
            print(f"Error al obtener IGV actual: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_igv(self, porcentaje, descripcion, fecha_inicio):
        """Crea una nueva tasa de IGV."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO igv (porcentaje, descripcion, fecha_inicio)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (porcentaje, descripcion, fecha_inicio))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al crear IGV: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_igv(self, id_igv):
        """Elimina una tasa de IGV."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "DELETE FROM igv WHERE id_igv = %s"
            cursor.execute(query, (id_igv,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar IGV: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)