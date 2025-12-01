import mysql.connector
from app.database import get_db_connection, close_db_connection

class EmpresaModel:
    def __init__(self):
        pass

    def get_empresa(self):
        """Obtiene la información de la empresa."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT e.*, m.nombre as moneda_nombre, m.simbolo, m.codigo_iso
            FROM empresa e
            LEFT JOIN moneda m ON e.id_moneda_base = m.id_moneda
            LIMIT 1
            """
            cursor.execute(query)
            empresa = cursor.fetchone()
            return empresa
        except mysql.connector.Error as err:
            print(f"Error al obtener información de la empresa: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_empresa(self, razon_social, ruc, direccion, id_moneda_base):
        """Crea la información de la empresa."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO empresa (razon_social, ruc, direccion, id_moneda_base)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (razon_social, ruc, direccion, id_moneda_base))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al crear empresa: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_empresa(self, razon_social, ruc, direccion, id_moneda_base):
        """Actualiza la información de la empresa."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
            UPDATE empresa 
            SET razon_social = %s, ruc = %s, direccion = %s, id_moneda_base = %s
            """
            cursor.execute(query, (razon_social, ruc, direccion, id_moneda_base))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar empresa: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)