# app/models/marca_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection


class MarcaModel:
    def __init__(self):
        pass

    def get_all_marcas(self):
        """Obtiene todas las marcas de la tabla 'marcas'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_marca, nombre, descripcion FROM marca ORDER BY nombre"
            cursor.execute(query)
            marcas = cursor.fetchall()
            return marcas
        except mysql.connector.Error as err:
            print(f"Error al obtener todas las marcas: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_marca_by_id(self, id_marca):
        """Obtiene una marcas por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_marca, nombre, descripcion FROM marca WHERE id_marca = %s"
            cursor.execute(query, (id_marca,))
            marca = cursor.fetchone()
            return marca
        except mysql.connector.Error as err:
            print(f"Error al obtener marcas por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_marca(self, nombre, descripcion):
        """Crea una nueva marcas en la tabla 'marcas'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación simple para evitar marcas duplicadas por nombre
            check_query = "SELECT COUNT(*) FROM marca WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(check_query, (nombre,))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de la marcas ya existe.")
                return False

            query = "INSERT INTO marca (nombre, descripcion) VALUES (%s, %s)"
            cursor.execute(query, (nombre, descripcion))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear marcas: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_marca(self, id_marca, nombre, descripcion):
        """Actualiza una marcas existente en la tabla 'marcas'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en el nombre (excluyendo la marcas actual)
            check_query = "SELECT COUNT(*) FROM marca WHERE LOWER(nombre) = LOWER(%s) AND id_marca != %s"
            cursor.execute(check_query, (nombre, id_marca))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de la marcas ya existe en otro registro.")
                return False

            query = "UPDATE marca SET nombre = %s, descripcion = %s WHERE id_marca = %s"
            cursor.execute(query, (nombre, descripcion, id_marca))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar marcas: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_marca(self, id_marca):
        """Elimina una marcas de la tabla 'marcas'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # NOTA: Debes verificar la integridad referencial (si hay productos usando esta marcas)
            # antes de permitir la eliminación en un sistema de producción.
            query = "DELETE FROM marca WHERE id_marca = %s"
            cursor.execute(query, (id_marca,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar marcas: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)