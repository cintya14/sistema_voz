# app/models/categoria_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection


class CategoriaModel:
    def __init__(self):
        pass

    def get_all_categorias(self):
        """Obtiene todas las categorías de la tabla 'categoria'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_categoria, nombre, descripcion FROM categoria ORDER BY nombre"
            cursor.execute(query)
            categorias = cursor.fetchall()
            return categorias
        except mysql.connector.Error as err:
            print(f"Error al obtener todas las categorías: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_categoria_by_id(self, id_categoria):
        """Obtiene una categoría por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_categoria, nombre, descripcion FROM categoria WHERE id_categoria = %s"
            cursor.execute(query, (id_categoria,))
            categoria = cursor.fetchone()
            return categoria
        except mysql.connector.Error as err:
            print(f"Error al obtener categoría por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_categoria(self, nombre, descripcion):
        """Crea una nueva categoría en la tabla 'categoria'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación simple para evitar categorías duplicadas por nombre
            check_query = "SELECT COUNT(*) FROM categoria WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(check_query, (nombre,))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de la categoría ya existe.")
                return False

            query = "INSERT INTO categoria (nombre, descripcion) VALUES (%s, %s)"
            cursor.execute(query, (nombre, descripcion))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear categoría: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_categoria(self, id_categoria, nombre, descripcion):
        """Actualiza una categoría existente en la tabla 'categoria'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en el nombre (excluyendo la categoría actual)
            check_query = "SELECT COUNT(*) FROM categoria WHERE LOWER(nombre) = LOWER(%s) AND id_categoria != %s"
            cursor.execute(check_query, (nombre, id_categoria))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre de la categoría ya existe en otro registro.")
                return False

            query = "UPDATE categoria SET nombre = %s, descripcion = %s WHERE id_categoria = %s"
            cursor.execute(query, (nombre, descripcion, id_categoria))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar categoría: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_categoria(self, id_categoria):
        """Elimina una categoría de la tabla 'categoria'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # NOTA: En un sistema de inventario real, debes verificar
            # la integridad referencial (ej: si hay productos en esta categoría).
            query = "DELETE FROM categoria WHERE id_categoria = %s"
            cursor.execute(query, (id_categoria,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar categoría: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)