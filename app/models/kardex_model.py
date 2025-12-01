import mysql.connector
from app.database import get_db_connection, close_db_connection


class KardexModel:
    def __init__(self):
        pass

    def get_kardex_articulo(self, id_articulo, id_almacen=None, fecha_inicio=None, fecha_fin=None):
        """Obtiene el kardex de un artículo específico."""
        print(f"DEBUG: Obteniendo kardex para artículo {id_articulo}, almacén {id_almacen}")

        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT k.*, \
                           a.nombre  as articulo_nombre, \
                           a.codigo  as articulo_codigo, \
                           al.nombre as almacen_nombre, \
                           tm.nombre as tipo_movimiento, \
                           tm.es_entrada
                    FROM kardex k
                             INNER JOIN articulo a ON k.id_articulo = a.id_articulo
                             INNER JOIN almacen al ON k.id_almacen = al.id_almacen
                             INNER JOIN tipo_movimiento tm ON k.id_tipo_movimiento = tm.id_tipo_movimiento
                    WHERE k.id_articulo = %s \
                    """
            params = [id_articulo]

            if id_almacen:
                query += " AND k.id_almacen = %s"
                params.append(id_almacen)

            if fecha_inicio:
                query += " AND DATE(k.fecha) >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND DATE(k.fecha) <= %s"
                params.append(fecha_fin)

            query += " ORDER BY k.fecha ASC, k.id_kardex ASC"

            print(f"DEBUG: Ejecutando query: {query}")
            print(f"DEBUG: Parámetros: {params}")

            cursor.execute(query, params)
            kardex = cursor.fetchall()

            print(f"DEBUG: Se encontraron {len(kardex)} registros en kardex")
            return kardex

        except mysql.connector.Error as err:
            print(f"ERROR: Error al obtener kardex por artículo: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_kardex_almacen(self, id_almacen, fecha_inicio=None, fecha_fin=None):
        """Obtiene el kardex de un almacén específico."""
        print(f"DEBUG: Obteniendo kardex para almacén {id_almacen}")

        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT k.*, \
                           a.nombre  as articulo_nombre, \
                           a.codigo  as articulo_codigo, \
                           tm.nombre as tipo_movimiento, \
                           tm.es_entrada
                    FROM kardex k
                             INNER JOIN articulo a ON k.id_articulo = a.id_articulo
                             INNER JOIN tipo_movimiento tm ON k.id_tipo_movimiento = tm.id_tipo_movimiento
                    WHERE k.id_almacen = %s \
                    """
            params = [id_almacen]

            if fecha_inicio:
                query += " AND DATE(k.fecha) >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND DATE(k.fecha) <= %s"
                params.append(fecha_fin)

            query += " ORDER BY k.fecha ASC, k.id_kardex ASC"

            print(f"DEBUG: Ejecutando query: {query}")
            print(f"DEBUG: Parámetros: {params}")

            cursor.execute(query, params)
            kardex = cursor.fetchall()

            print(f"DEBUG: Se encontraron {len(kardex)} registros en kardex")
            return kardex

        except mysql.connector.Error as err:
            print(f"ERROR: Error al obtener kardex por almacén: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_saldo_actual_articulo(self, id_articulo, id_almacen):
        """Obtiene el saldo actual de un artículo en un almacén."""
        conn = get_db_connection()
        if conn is None:
            return 0
        cursor = conn.cursor()
        try:
            query = """
                    SELECT cantidad_saldo
                    FROM kardex
                    WHERE id_articulo = %s \
                      AND id_almacen = %s
                    ORDER BY fecha DESC, id_kardex DESC LIMIT 1 \
                    """
            cursor.execute(query, (id_articulo, id_almacen))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except mysql.connector.Error as err:
            print(f"Error al obtener saldo actual: {err}")
            return 0
        finally:
            cursor.close()
            close_db_connection(conn)