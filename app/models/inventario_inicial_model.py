import mysql.connector
from app.database import get_db_connection, close_db_connection
from datetime import datetime

class InventarioInicialModel:
    def __init__(self):
        pass

    def get_all_inventario_inicial(self):
        """Obtiene todos los registros de inventario inicial."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                ii.*,
                a.nombre as articulo_nombre,
                a.codigo as articulo_codigo,
                al.nombre as almacen_nombre
            FROM inventario_inicial ii
            INNER JOIN articulo a ON ii.id_articulo = a.id_articulo
            INNER JOIN almacen al ON ii.id_almacen = al.id_almacen
            ORDER BY ii.fecha DESC, al.nombre
            """
            cursor.execute(query)
            inventario = cursor.fetchall()
            return inventario
        except mysql.connector.Error as err:
            print(f"Error al obtener inventario inicial: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_inventario_inicial_by_id(self, id_inventario_inicial):
        """Obtiene un registro de inventario inicial por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                ii.*,
                a.nombre as articulo_nombre,
                a.codigo as articulo_codigo,
                al.nombre as almacen_nombre
            FROM inventario_inicial ii
            INNER JOIN articulo a ON ii.id_articulo = a.id_articulo
            INNER JOIN almacen al ON ii.id_almacen = al.id_almacen
            WHERE ii.id_inventario_inicial = %s
            """
            cursor.execute(query, (id_inventario_inicial,))
            inventario = cursor.fetchone()
            return inventario
        except mysql.connector.Error as err:
            print(f"Error al obtener inventario inicial por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def existe_inventario_inicial(self, id_articulo, id_almacen):
        """Verifica si ya existe inventario inicial para un artículo en un almacén."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "SELECT COUNT(*) FROM inventario_inicial WHERE id_articulo = %s AND id_almacen = %s"
            cursor.execute(query, (id_articulo, id_almacen))
            count = cursor.fetchone()[0]
            return count > 0
        except mysql.connector.Error as err:
            print(f"Error al verificar inventario inicial: {err}")
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_inventario_inicial(self, fecha, id_almacen, id_articulo, cantidad, costo_unitario):
        """Crea un nuevo registro de inventario inicial."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si ya existe registro para este artículo en el almacén
            check_query = """
            SELECT COUNT(*) FROM inventario_inicial 
            WHERE id_almacen = %s AND id_articulo = %s
            """
            cursor.execute(check_query, (id_almacen, id_articulo))
            if cursor.fetchone()[0] > 0:
                return False

            query = """
            INSERT INTO inventario_inicial (fecha, id_almacen, id_articulo, cantidad, costo_unitario)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (fecha, id_almacen, id_articulo, cantidad, costo_unitario))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear inventario inicial: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_inventario_inicial(self, id_inventario_inicial, cantidad, costo_unitario):
        """Actualiza un registro de inventario inicial."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
            UPDATE inventario_inicial 
            SET cantidad = %s, costo_unitario = %s 
            WHERE id_inventario_inicial = %s
            """
            cursor.execute(query, (cantidad, costo_unitario, id_inventario_inicial))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar inventario inicial: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_inventario_inicial(self, id_inventario_inicial):
        """NO IMPLEMENTADO - Por seguridad del sistema."""
        print(f"⚠️  INTENTO DE ELIMINACIÓN BLOQUEADO: Inventario inicial ID {id_inventario_inicial}")
        return False  # Siempre retorna False para bloquear eliminaciones