import mysql.connector
from app.database import get_db_connection, close_db_connection


class StockAlmacenModel:
    def __init__(self):
        pass

    def get_all_stock(self):
        """Obtiene todo el stock con información de artículos y almacenes."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT sa.id_articulo, \
                           sa.id_almacen, \
                           a.codigo  as articulo_codigo, \
                           a.nombre  as articulo_nombre, \
                           al.nombre as almacen_nombre, \
                           sa.stock_actual, \
                           a.stock_minimo, \
                           CASE \
                               WHEN sa.stock_actual <= a.stock_minimo THEN 'CRÍTICO' \
                               WHEN sa.stock_actual <= a.stock_minimo * 1.5 THEN 'BAJO' \
                               ELSE 'NORMAL' \
                               END   as estado_stock
                    FROM stock_almacen sa
                             INNER JOIN articulo a ON sa.id_articulo = a.id_articulo
                             INNER JOIN almacen al ON sa.id_almacen = al.id_almacen
                    ORDER BY al.nombre, a.nombre \
                    """
            cursor.execute(query)
            stock = cursor.fetchall()
            return stock
        except mysql.connector.Error as err:
            print(f"Error al obtener stock: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_stock_by_almacen(self, id_almacen):
        """Obtiene el stock de un almacén específico."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT sa.id_articulo, \
                           a.codigo as articulo_codigo, \
                           a.nombre as articulo_nombre, \
                           sa.stock_actual, \
                           a.stock_minimo
                    FROM stock_almacen sa
                             INNER JOIN articulo a ON sa.id_articulo = a.id_articulo
                    WHERE sa.id_almacen = %s
                    ORDER BY a.nombre \
                    """
            cursor.execute(query, (id_almacen,))
            stock = cursor.fetchall()
            return stock
        except mysql.connector.Error as err:
            print(f"Error al obtener stock por almacén: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_stock(self, id_articulo, id_almacen, cantidad):
        """Actualiza el stock de un artículo en un almacén."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Verificar si existe el registro
            check_query = "SELECT COUNT(*) FROM stock_almacen WHERE id_articulo = %s AND id_almacen = %s"
            cursor.execute(check_query, (id_articulo, id_almacen))

            if cursor.fetchone()[0] > 0:
                # Actualizar stock existente
                query = "UPDATE stock_almacen SET stock_actual = %s WHERE id_articulo = %s AND id_almacen = %s"
                cursor.execute(query, (cantidad, id_articulo, id_almacen))
            else:
                # Insertar nuevo registro - ORDEN CORREGIDO
                query = "INSERT INTO stock_almacen (id_articulo, id_almacen, stock_actual) VALUES (%s, %s, %s)"
                # ORDEN CORRECTO: (id_articulo, id_almacen, cantidad)
                cursor.execute(query, (id_articulo, id_almacen, cantidad))

            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al actualizar stock: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_stock_bajo(self):
        """Obtiene artículos con stock bajo o crítico."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT sa.id_articulo, \
                           sa.id_almacen, \
                           a.codigo, \
                           a.nombre                           as articulo_nombre, \
                           al.nombre                          as almacen_nombre, \
                           sa.stock_actual, \
                           a.stock_minimo, \
                           (a.stock_minimo - sa.stock_actual) as faltante
                    FROM stock_almacen sa
                             INNER JOIN articulo a ON sa.id_articulo = a.id_articulo
                             INNER JOIN almacen al ON sa.id_almacen = al.id_almacen
                    WHERE sa.stock_actual <= a.stock_minimo
                    ORDER BY faltante DESC \
                    """
            cursor.execute(query)
            stock_bajo = cursor.fetchall()
            return stock_bajo
        except mysql.connector.Error as err:
            print(f"Error al obtener stock bajo: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def actualizar_stock_inventario_inicial(self, id_articulo, id_almacen, cantidad):
        """Actualiza el stock desde inventario inicial - VERSIÓN SIMPLIFICADA"""
        conn = get_db_connection()
        if conn is None:
            return False

        cursor = conn.cursor()
        try:
            print(f"ACTUALIZANDO STOCK - Artículo: {id_articulo}, Almacén: {id_almacen}, Cantidad: {cantidad}")

            # VERIFICAR SI EXISTE
            check_query = "SELECT stock_actual FROM stock_almacen WHERE id_articulo = %s AND id_almacen = %s"
            cursor.execute(check_query, (id_articulo, id_almacen))
            resultado = cursor.fetchone()

            if resultado:
                # ACTUALIZAR existente - REEMPLAZAR con el valor del inventario inicial
                update_query = "UPDATE stock_almacen SET stock_actual = %s WHERE id_articulo = %s AND id_almacen = %s"
                cursor.execute(update_query, (cantidad, id_articulo, id_almacen))
                print(f"Stock ACTUALIZADO a {cantidad}")
            else:
                # INSERTAR nuevo
                insert_query = "INSERT INTO stock_almacen (id_articulo, id_almacen, stock_actual) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (id_articulo, id_almacen, cantidad))
                print(f"Nuevo stock CREADO: {cantidad}")

            conn.commit()
            return True

        except Exception as e:
            print(f"ERROR actualizando stock: {e}")
            conn.rollback()
            return False
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

    # En tu StockAlmacenModel, agrega este método:
    def get_stock_by_articulo(self, id_articulo):
        """Obtiene el stock total de un artículo en todos los almacenes"""
        conn = get_db_connection()
        if conn is None:
            return {"stock_total": 0}

        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT COALESCE(SUM(stock_actual), 0) as stock_total
                    FROM stock_almacen
                    WHERE id_articulo = %s \
                    """
            cursor.execute(query, (id_articulo,))
            result = cursor.fetchone()
            return result if result else {"stock_total": 0}
        except Exception as e:
            print(f"Error al obtener stock del artículo {id_articulo}: {e}")
            return {"stock_total": 0}
        finally:
            cursor.close()
            close_db_connection(conn)

