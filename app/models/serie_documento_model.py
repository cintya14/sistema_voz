import mysql.connector
from app.database import get_db_connection, close_db_connection

class SerieDocumentoModel:
    def __init__(self):
        pass

    def get_all_series_documento(self):
        """Obtiene todas las series de documento con información del tipo de documento."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT sd.*, td.nombre as tipo_documento_nombre
                FROM serie_documento sd
                INNER JOIN tipo_documento td ON sd.id_tipo_documento = td.id_tipo_documento
                ORDER BY td.nombre, sd.serie
            """
            cursor.execute(query)
            series = cursor.fetchall()
            return series
        except mysql.connector.Error as err:
            print(f"Error al obtener todas las series de documento: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_serie_documento_by_id(self, id_serie):
        """Obtiene una serie de documento por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT sd.*, td.nombre as tipo_documento_nombre
                FROM serie_documento sd
                INNER JOIN tipo_documento td ON sd.id_tipo_documento = td.id_tipo_documento
                WHERE sd.id_serie = %s
            """
            cursor.execute(query, (id_serie,))
            serie = cursor.fetchone()
            return serie
        except mysql.connector.Error as err:
            print(f"Error al obtener serie de documento por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_series_por_tipo_documento(self, id_tipo_documento):
        """Obtiene las series de documento por tipo de documento."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM serie_documento WHERE id_tipo_documento = %s ORDER BY serie"
            cursor.execute(query, (id_tipo_documento,))
            series = cursor.fetchall()
            return series
        except mysql.connector.Error as err:
            print(f"Error al obtener series por tipo de documento: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_serie_documento(self, id_tipo_documento, serie, correlativo_actual=0):
        """Crea una nueva serie de documento."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si ya existe la serie para el mismo tipo de documento
            check_query = "SELECT COUNT(*) FROM serie_documento WHERE id_tipo_documento = %s AND serie = %s"
            cursor.execute(check_query, (id_tipo_documento, serie))
            if cursor.fetchone()[0] > 0:
                print("Error: Ya existe una serie con el mismo código para este tipo de documento.")
                return False

            query = "INSERT INTO serie_documento (id_tipo_documento, serie, correlativo_actual) VALUES (%s, %s, %s)"
            cursor.execute(query, (id_tipo_documento, serie, correlativo_actual))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear serie de documento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_serie_documento(self, id_serie, id_tipo_documento, serie, correlativo_actual):
        """Actualiza una serie de documento existente."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si ya existe otra serie con el mismo código para el mismo tipo de documento (excluyendo la actual)
            check_query = "SELECT COUNT(*) FROM serie_documento WHERE id_tipo_documento = %s AND serie = %s AND id_serie != %s"
            cursor.execute(check_query, (id_tipo_documento, serie, id_serie))
            if cursor.fetchone()[0] > 0:
                print("Error: Ya existe otra serie con el mismo código para este tipo de documento.")
                return False

            query = "UPDATE serie_documento SET id_tipo_documento = %s, serie = %s, correlativo_actual = %s WHERE id_serie = %s"
            cursor.execute(query, (id_tipo_documento, serie, correlativo_actual, id_serie))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar serie de documento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_serie_documento(self, id_serie):
        """Elimina una serie de documento."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si la serie está siendo usada en ventas (u otros documentos) antes de eliminar?
            # Por ahora, eliminación directa.
            query = "DELETE FROM serie_documento WHERE id_serie = %s"
            cursor.execute(query, (id_serie,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar serie de documento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def incrementar_correlativo(self, id_serie):
        """Incrementa el correlativo actual de una serie."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "UPDATE serie_documento SET correlativo_actual = correlativo_actual + 1 WHERE id_serie = %s"
            cursor.execute(query, (id_serie,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al incrementar correlativo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)