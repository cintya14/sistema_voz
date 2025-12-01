# app/models/unidad_medida_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection


class UnidadMedidaModel:
    def __init__(self):
        pass

    def get_all_unidades_medida(self):
        """Obtiene todas las unidades de medida de la tabla 'unidad_medida'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_unidad_medida, nombre, abreviatura FROM unidad_medida ORDER BY nombre"
            cursor.execute(query)
            unidades = cursor.fetchall()
            return unidades
        except mysql.connector.Error as err:
            print(f"Error al obtener todas las unidades de medida: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_unidad_medida_by_id(self, id_unidad_medida):
        """Obtiene una unidad de medida por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_unidad_medida, nombre, abreviatura FROM unidad_medida WHERE id_unidad_medida = %s"
            cursor.execute(query, (id_unidad_medida,))
            unidad = cursor.fetchone()
            return unidad
        except mysql.connector.Error as err:
            print(f"Error al obtener unidad de medida por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_unidad_medida(self, nombre, abreviatura):
        """Crea una nueva unidad de medida en la tabla 'unidad_medida'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar unidades duplicadas por nombre o abreviatura
            check_query = "SELECT COUNT(*) FROM unidad_medida WHERE LOWER(nombre) = LOWER(%s) OR LOWER(abreviatura) = LOWER(%s)"
            cursor.execute(check_query, (nombre, abreviatura))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre o la abreviatura de la unidad de medida ya existe.")
                return False

            query = "INSERT INTO unidad_medida (nombre, abreviatura) VALUES (%s, %s)"
            cursor.execute(query, (nombre, abreviatura))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear unidad de medida: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_unidad_medida(self, id_unidad_medida, nombre, abreviatura):
        """Actualiza una unidad de medida existente en la tabla 'unidad_medida'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en nombre o abreviatura (excluyendo la unidad actual)
            check_query = "SELECT COUNT(*) FROM unidad_medida WHERE (LOWER(nombre) = LOWER(%s) OR LOWER(abreviatura) = LOWER(%s)) AND id_unidad_medida != %s"
            cursor.execute(check_query, (nombre, abreviatura, id_unidad_medida))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre o la abreviatura ya existen en otro registro.")
                return False

            query = "UPDATE unidad_medida SET nombre = %s, abreviatura = %s WHERE id_unidad_medida = %s"
            cursor.execute(query, (nombre, abreviatura, id_unidad_medida))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar unidad de medida: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_unidad_medida(self, id_unidad_medida):
        """Elimina una unidad de medida de la tabla 'unidad_medida'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # NOTA: En un sistema real, antes de borrar, se debe verificar
            # la integridad referencial (ej: si hay productos usando esta unidad).
            query = "DELETE FROM unidad_medida WHERE id_unidad_medida = %s"
            cursor.execute(query, (id_unidad_medida,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar unidad de medida: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)