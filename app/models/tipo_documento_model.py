# app/models/tipo_documento_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection


class TipoDocumentoModel:
    def __init__(self):
        pass

    def get_all_tipos_documento(self):
        """Obtiene todos los tipos de documento de la tabla 'tipo_documento'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_tipo_documento, nombre, codigo_sunat FROM tipo_documento ORDER BY id_tipo_documento"
            cursor.execute(query)
            tipos_documento = cursor.fetchall()
            return tipos_documento
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los tipos de documento: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_tipo_documento_by_id(self, id_tipo_documento):
        """Obtiene un tipo de documento por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_tipo_documento, nombre, codigo_sunat FROM tipo_documento WHERE id_tipo_documento = %s"
            cursor.execute(query, (id_tipo_documento,))
            tipo_documento = cursor.fetchone()
            return tipo_documento
        except mysql.connector.Error as err:
            print(f"Error al obtener tipo de documento por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_tipo_documento(self, nombre, codigo_sunat):
        """Crea un nuevo tipo de documento en la tabla 'tipo_documento'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en nombre O código_sunat
            check_query = "SELECT COUNT(*) FROM tipo_documento WHERE LOWER(nombre) = LOWER(%s) OR LOWER(codigo_sunat) = LOWER(%s)"
            cursor.execute(check_query, (nombre, codigo_sunat))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre o el código SUNAT ya existen.")
                return False

            query = "INSERT INTO tipo_documento (nombre, codigo_sunat) VALUES (%s, %s)"
            cursor.execute(query, (nombre, codigo_sunat))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear tipo de documento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_tipo_documento(self, id_tipo_documento, nombre, codigo_sunat):
        """Actualiza un tipo de documento existente en la tabla 'tipo_documento'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en nombre O código_sunat (excluyendo el actual)
            check_query = "SELECT COUNT(*) FROM tipo_documento WHERE (LOWER(nombre) = LOWER(%s) OR LOWER(codigo_sunat) = LOWER(%s)) AND id_tipo_documento != %s"
            cursor.execute(check_query, (nombre, codigo_sunat, id_tipo_documento))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre o el código SUNAT ya existen en otro registro.")
                return False

            query = "UPDATE tipo_documento SET nombre = %s, codigo_sunat = %s WHERE id_tipo_documento = %s"
            cursor.execute(query, (nombre, codigo_sunat, id_tipo_documento))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar tipo de documento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_tipo_documento(self, id_tipo_documento):
        """Elimina un tipo de documento de la tabla 'tipo_documento'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # NOTA: En un sistema real, se debe verificar la integridad referencial
            # (ej: si hay clientes, proveedores o documentos que usan este tipo).
            query = "DELETE FROM tipo_documento WHERE id_tipo_documento = %s"
            cursor.execute(query, (id_tipo_documento,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar tipo de documento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)