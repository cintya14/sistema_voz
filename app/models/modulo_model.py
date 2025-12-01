# app/models/modulo_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection


class ModuloModel:
    def __init__(self):
        pass

    def get_all_modulos(self):
        """Obtiene todos los módulos de la tabla 'modulo'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_modulo, nombre FROM modulo ORDER BY nombre"
            cursor.execute(query)
            modulos = cursor.fetchall()
            return modulos
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los módulos: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_modulo_by_id(self, id_modulo):
        """Obtiene un módulo por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_modulo, nombre FROM modulo WHERE id_modulo = %s"
            cursor.execute(query, (id_modulo,))
            modulo = cursor.fetchone()
            return modulo
        except mysql.connector.Error as err:
            print(f"Error al obtener módulo por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_modulo(self, nombre):
        """Crea un nuevo módulo en la tabla 'modulo'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar módulos duplicados por nombre
            check_query = "SELECT COUNT(*) FROM modulo WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(check_query, (nombre,))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de módulo ya existe.")
                return False

            query = "INSERT INTO modulo (nombre) VALUES (%s)"
            cursor.execute(query, (nombre,))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear módulo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_modulo(self, id_modulo, nombre):
        """Actualiza un módulo existente en la tabla 'modulo'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en el nombre (excluyendo el módulo actual)
            check_query = "SELECT COUNT(*) FROM modulo WHERE LOWER(nombre) = LOWER(%s) AND id_modulo != %s"
            cursor.execute(check_query, (nombre, id_modulo))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de módulo ya existe en otro registro.")
                return False

            query = "UPDATE modulo SET nombre = %s WHERE id_modulo = %s"
            cursor.execute(query, (nombre, id_modulo))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar módulo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_modulo(self, id_modulo):
        """Elimina un módulo de la tabla 'modulo'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Considera que en un sistema real, un módulo podría estar ligado a permisos.
            query = "DELETE FROM modulo WHERE id_modulo = %s"
            cursor.execute(query, (id_modulo,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar módulo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)