import mysql.connector
from app.database import get_db_connection, close_db_connection


class ReporteModel:
    def __init__(self):
        pass

    def get_articulos_para_reporte(self):
        """Obtiene artículos para select de reportes."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT id_articulo, codigo, nombre
                    FROM articulo
                    WHERE estado = 'ACTIVO'
                    ORDER BY nombre \
                    """
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener artículos: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_almacenes(self):
        """Obtiene almacenes para select de reportes."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_almacen, nombre FROM almacen ORDER BY nombre"
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener almacenes: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_tipos_movimiento(self):
        """Obtiene tipos de movimiento para reportes."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_tipo_movimiento, nombre FROM tipo_movimiento ORDER BY nombre"
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener tipos de movimiento: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_kardex_articulo(self, id_articulo, id_almacen, fecha_desde, fecha_hasta):
        """Obtiene datos de kardex para un artículo."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT k.fecha, \
                           a.nombre  as articulo, \
                           al.nombre as almacen,
                           tm.nombre as tipo_movimiento, \
                           k.tipo_documento, \
                           k.numero_documento,
                           k.cantidad_entrada, \
                           k.cantidad_salida, \
                           k.cantidad_saldo,
                           k.costo_promedio, \
                           k.valor_saldo
                    FROM kardex k
                             JOIN articulo a ON k.id_articulo = a.id_articulo
                             JOIN almacen al ON k.id_almacen = al.id_almacen
                             JOIN tipo_movimiento tm ON k.id_tipo_movimiento = tm.id_tipo_movimiento
                    WHERE k.id_articulo = %s \
                      AND k.id_almacen = %s
                      AND k.fecha BETWEEN %s AND %s
                    ORDER BY k.fecha, k.id_kardex \
                    """
            cursor.execute(query, (id_articulo, id_almacen, fecha_desde, fecha_hasta))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener kardex: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_stock_almacen(self, id_almacen, stock_minimo=False):
        """Obtiene stock actual por almacén."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            base_query = """
                         SELECT a.codigo, \
                                a.nombre       as articulo, \
                                c.nombre       as categoria,
                                m.nombre       as marca, \
                                um.abreviatura as unidad,
                                s.stock_actual, \
                                a.stock_minimo, \
                                a.precio_compra, \
                                a.precio_venta
                         FROM stock_almacen s
                                  JOIN articulo a ON s.id_articulo = a.id_articulo
                                  LEFT JOIN categoria c ON a.id_categoria = c.id_categoria
                                  LEFT JOIN marca m ON a.id_marca = m.id_marca
                                  LEFT JOIN unidad_medida um ON a.id_unidad_medida = um.id_unidad_medida
                         WHERE s.id_almacen = %s \
                           AND a.estado = 'ACTIVO' \
                         """

            if stock_minimo:
                base_query += " AND s.stock_actual <= a.stock_minimo"

            base_query += " ORDER BY a.nombre"

            cursor.execute(base_query, (id_almacen,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener stock: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_movimientos_periodo(self, id_tipo_movimiento, id_almacen, fecha_desde, fecha_hasta):
        """Obtiene movimientos por período."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT mc.fecha_movimiento, \
                           tm.nombre                         as tipo_movimiento,
                           al.nombre                         as almacen, \
                           a.codigo, \
                           a.nombre                          as articulo,
                           md.cantidad, \
                           md.costo_unitario,
                           (md.cantidad * md.costo_unitario) as total,
                           u.nombre                          as usuario, \
                           p.razon_social                    as proveedor
                    FROM movimiento_cabecera mc
                             JOIN tipo_movimiento tm ON mc.id_tipo_movimiento = tm.id_tipo_movimiento
                             JOIN almacen al ON mc.id_almacen = al.id_almacen
                             JOIN movimiento_detalle md ON mc.id_movimiento_cabecera = md.id_movimiento_cabecera
                             JOIN articulo a ON md.id_articulo = a.id_articulo
                             JOIN usuario u ON mc.id_usuario_registro = u.id_usuario
                             LEFT JOIN proveedor p ON mc.id_proveedor = p.id_proveedor
                    WHERE mc.fecha_movimiento BETWEEN %s AND %s \
                    """

            params = [fecha_desde, fecha_hasta]

            if id_tipo_movimiento:
                query += " AND mc.id_tipo_movimiento = %s"
                params.append(id_tipo_movimiento)

            if id_almacen:
                query += " AND mc.id_almacen = %s"
                params.append(id_almacen)

            query += " ORDER BY mc.fecha_movimiento DESC"

            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener movimientos: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)