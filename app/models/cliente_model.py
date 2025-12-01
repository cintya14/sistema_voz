import mysql.connector
from app.database import get_db_connection, close_db_connection

class ClienteModel:
    def __init__(self):
        pass

    def get_all_clientes(self):
        """Obtiene todos los clientes activos."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM cliente WHERE estado = 'ACTIVO' ORDER BY nombre_o_razon_social"
            cursor.execute(query)
            clientes = cursor.fetchall()
            return clientes
        except mysql.connector.Error as err:
            print(f"Error al obtener clientes: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_cliente_by_id(self, id_cliente):
        """Obtiene un cliente por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM cliente WHERE id_cliente = %s"
            cursor.execute(query, (id_cliente,))
            cliente = cursor.fetchone()
            return cliente
        except mysql.connector.Error as err:
            print(f"Error al obtener cliente: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_cliente(self, tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo):
        """Crea un nuevo cliente."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validar que no exista el número de documento
            check_query = "SELECT COUNT(*) FROM cliente WHERE numero_documento = %s"
            cursor.execute(check_query, (numero_documento,))
            if cursor.fetchone()[0] > 0:
                return False

            query = """
            INSERT INTO cliente (tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear cliente: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_cliente(self, id_cliente, tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo):
        """Actualiza un cliente existente."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validar que no exista el número de documento en otro cliente
            check_query = "SELECT COUNT(*) FROM cliente WHERE numero_documento = %s AND id_cliente != %s"
            cursor.execute(check_query, (numero_documento, id_cliente))
            if cursor.fetchone()[0] > 0:
                return False

            query = """
            UPDATE cliente 
            SET tipo_documento = %s, numero_documento = %s, nombre_o_razon_social = %s, 
                direccion = %s, telefono = %s, correo = %s
            WHERE id_cliente = %s
            """
            cursor.execute(query, (tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo, id_cliente))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar cliente: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_cliente(self, id_cliente):
        """Elimina un cliente (cambia estado a INACTIVO)."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "UPDATE cliente SET estado = 'INACTIVO' WHERE id_cliente = %s"
            cursor.execute(query, (id_cliente,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar cliente: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)