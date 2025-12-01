# app/models/rol_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection


class RolModel:
    def __init__(self):
        pass

    def get_all_roles(self):
        """Obtiene todos los roles de la tabla 'rol'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_rol, nombre FROM rol ORDER BY nombre"
            cursor.execute(query)
            roles = cursor.fetchall()
            return roles
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los roles: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_rol_by_id(self, id_rol):
        """Obtiene un rol por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_rol, nombre FROM rol WHERE id_rol = %s"
            cursor.execute(query, (id_rol,))
            rol = cursor.fetchone()
            return rol
        except mysql.connector.Error as err:
            print(f"Error al obtener rol por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_rol(self, nombre):
        """Crea un nuevo rol en la tabla 'rol'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación simple para evitar roles duplicados por nombre
            check_query = "SELECT COUNT(*) FROM rol WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(check_query, (nombre,))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de rol ya existe.")
                return False

            query = "INSERT INTO rol (nombre) VALUES (%s)"
            cursor.execute(query, (nombre,))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear rol: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_rol(self, id_rol, nombre):
        """Actualiza un rol existente en la tabla 'rol'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en el nombre (excluyendo el rol actual)
            check_query = "SELECT COUNT(*) FROM rol WHERE LOWER(nombre) = LOWER(%s) AND id_rol != %s"
            cursor.execute(check_query, (nombre, id_rol))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de rol ya existe en otro registro.")
                return False

            query = "UPDATE rol SET nombre = %s WHERE id_rol = %s"
            cursor.execute(query, (nombre, id_rol))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar rol: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_rol(self, id_rol):
        """Elimina un rol de la tabla 'rol'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # **NOTA DE SEGURIDAD**: En un sistema real, deberías
            # primero verificar si hay usuarios (o cualquier otra tabla)
            # vinculados a este rol antes de eliminarlo.
            query = "DELETE FROM rol WHERE id_rol = %s"
            cursor.execute(query, (id_rol,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar rol: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)