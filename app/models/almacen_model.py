import mysql.connector
from app.database import get_db_connection, close_db_connection

class AlmacenModel:
    def __init__(self):
        pass

    def get_all_almacenes(self):
        """Obtiene todos los almacenes de la tabla 'almacen'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM almacen ORDER BY nombre"
            cursor.execute(query)
            almacenes = cursor.fetchall()
            return almacenes
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los almacenes: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_almacen_by_id(self, id_almacen):
        """Obtiene un almacén por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM almacen WHERE id_almacen = %s"
            cursor.execute(query, (id_almacen,))
            almacen = cursor.fetchone()
            return almacen
        except mysql.connector.Error as err:
            print(f"Error al obtener almacén por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_almacen(self, nombre, direccion, es_principal):
        """Crea un nuevo almacén en la tabla 'almacen'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación simple para evitar almacenes duplicados por nombre
            check_query = "SELECT COUNT(*) FROM almacen WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(check_query, (nombre,))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre del almacén ya existe.")
                return False

            # Si este almacén será principal, quitar principal a los demás
            if es_principal:
                update_query = "UPDATE almacen SET es_principal = 0 WHERE es_principal = 1"
                cursor.execute(update_query)

            query = "INSERT INTO almacen (nombre, direccion, es_principal) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, direccion, es_principal))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear almacén: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_almacen(self, id_almacen, nombre, direccion, es_principal):
        """Actualiza un almacén existente en la tabla 'almacen'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en el nombre (excluyendo el almacén actual)
            check_query = "SELECT COUNT(*) FROM almacen WHERE LOWER(nombre) = LOWER(%s) AND id_almacen != %s"
            cursor.execute(check_query, (nombre, id_almacen))
            if cursor.fetchone()[0] > 0:
                print("Error: El nombre del almacén ya existe en otro registro.")
                return False

            # Si este almacén será principal, quitar principal a los demás
            if es_principal:
                update_query = "UPDATE almacen SET es_principal = 0 WHERE es_principal = 1 AND id_almacen != %s"
                cursor.execute(update_query, (id_almacen,))

            query = "UPDATE almacen SET nombre = %s, direccion = %s, es_principal = %s WHERE id_almacen = %s"
            cursor.execute(query, (nombre, direccion, es_principal, id_almacen))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar almacén: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_almacen(self, id_almacen):
        """Elimina un almacén de la tabla 'almacen'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # NOTA: En un sistema de inventario real, debes verificar
            # la integridad referencial (ej: si hay stock en este almacén).
            query = "DELETE FROM almacen WHERE id_almacen = %s"
            cursor.execute(query, (id_almacen,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar almacén: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_almacen_principal(self):
        """Obtiene el almacén principal."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM almacen WHERE es_principal = 1"
            cursor.execute(query)
            almacen = cursor.fetchone()
            return almacen
        except mysql.connector.Error as err:
            print(f"Error al obtener almacén principal: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)