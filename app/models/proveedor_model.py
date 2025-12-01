import mysql.connector
from app.database import get_db_connection, close_db_connection

class ProveedorModel:
    def __init__(self):
        pass

    def get_all_proveedores(self):
        """Obtiene todos los proveedores."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM proveedor ORDER BY razon_social"
            cursor.execute(query)
            proveedores = cursor.fetchall()
            return proveedores
        except mysql.connector.Error as err:
            print(f"Error al obtener proveedores: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_proveedor_by_id(self, id_proveedor):
        """Obtiene un proveedor por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM proveedor WHERE id_proveedor = %s"
            cursor.execute(query, (id_proveedor,))
            proveedor = cursor.fetchone()
            return proveedor
        except mysql.connector.Error as err:
            print(f"Error al obtener proveedor: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_proveedor(self, tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo):
        """Crea un nuevo proveedor."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validar que el número de documento no exista
            check_query = "SELECT COUNT(*) FROM proveedor WHERE numero_documento = %s"
            cursor.execute(check_query, (numero_documento,))
            if cursor.fetchone()[0] > 0:
                return False

            query = """
            INSERT INTO proveedor 
            (tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear proveedor: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_proveedor(self, id_proveedor, tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo):
        """Actualiza un proveedor existente."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validar que el número de documento no exista en otro proveedor
            check_query = "SELECT COUNT(*) FROM proveedor WHERE numero_documento = %s AND id_proveedor != %s"
            cursor.execute(check_query, (numero_documento, id_proveedor))
            if cursor.fetchone()[0] > 0:
                return False

            query = """
            UPDATE proveedor 
            SET tipo_documento = %s, numero_documento = %s, razon_social = %s, nombre_contacto = %s, 
                direccion = %s, telefono = %s, correo = %s
            WHERE id_proveedor = %s
            """
            cursor.execute(query, (tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo, id_proveedor))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar proveedor: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_proveedor(self, id_proveedor):
        """Elimina un proveedor (cambia estado a INACTIVO)."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "UPDATE proveedor SET estado = 'INACTIVO' WHERE id_proveedor = %s"
            cursor.execute(query, (id_proveedor,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar proveedor: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def activate_proveedor(self, id_proveedor):
        """Activa un proveedor (cambia estado a ACTIVO)."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "UPDATE proveedor SET estado = 'ACTIVO' WHERE id_proveedor = %s"
            cursor.execute(query, (id_proveedor,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al activar proveedor: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)