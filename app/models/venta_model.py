import mysql.connector
from app.database import get_db_connection, close_db_connection
from datetime import datetime


class VentaModel:
    def __init__(self):
        pass

    def get_all_ventas(self):
        """Obtiene todas las ventas."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT vc.*, \
                           td.nombre               as tipo_documento_nombre, \
                           s.serie                 as serie_documento, \
                           c.nombre_o_razon_social as cliente_nombre, \
                           u.nombre_usuario
                    FROM venta_cabecera vc
                             INNER JOIN tipo_documento td ON vc.id_tipo_documento = td.id_tipo_documento
                             INNER JOIN serie_documento s ON vc.id_serie = s.id_serie
                             LEFT JOIN cliente c ON vc.id_cliente = c.id_cliente
                             INNER JOIN usuario u ON vc.id_usuario_venta = u.id_usuario
                    ORDER BY vc.fecha_emision DESC \
                    """
            cursor.execute(query)
            ventas = cursor.fetchall()
            return ventas
        except mysql.connector.Error as err:
            print(f"Error al obtener ventas: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_venta_by_id(self, id_venta):
        """Obtiene una venta por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT vc.*, \
                           td.nombre               as tipo_documento_nombre, \
                           s.serie                 as serie_documento, \
                           c.nombre_o_razon_social as cliente_nombre, \
                           u.nombre_usuario
                    FROM venta_cabecera vc
                             INNER JOIN tipo_documento td ON vc.id_tipo_documento = td.id_tipo_documento
                             INNER JOIN serie_documento s ON vc.id_serie = s.id_serie
                             LEFT JOIN cliente c ON vc.id_cliente = c.id_cliente
                             INNER JOIN usuario u ON vc.id_usuario_venta = u.id_usuario
                    WHERE vc.id_venta = %s \
                    """
            cursor.execute(query, (id_venta,))
            venta = cursor.fetchone()
            return venta
        except mysql.connector.Error as err:
            print(f"Error al obtener venta: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_detalle_venta(self, id_venta):
        """Obtiene el detalle de una venta."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT vd.*, \
                           a.codigo, \
                           a.nombre      as articulo_nombre, \
                           u.nombre      as unidad_nombre, \
                           u.abreviatura as unidad_abreviatura
                    FROM venta_detalle vd
                             INNER JOIN articulo a ON vd.id_articulo = a.id_articulo
                             INNER JOIN unidad_medida u ON a.id_unidad_medida = u.id_unidad_medida
                    WHERE vd.id_venta = %s \
                    """
            cursor.execute(query, (id_venta,))
            detalle = cursor.fetchall()
            return detalle
        except mysql.connector.Error as err:
            print(f"Error al obtener detalle de venta: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_venta(self, fecha_emision, id_tipo_documento, id_serie, numero_documento, id_cliente, id_usuario,
                     total_gravado, total_igv, total_venta):
        """Crea una nueva venta."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
                    INSERT INTO venta_cabecera
                    (fecha_emision, id_tipo_documento, id_serie, numero_documento, id_cliente, id_usuario_venta, \
                     total_gravado, total_igv, total_venta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    """
            cursor.execute(query, (fecha_emision, id_tipo_documento, id_serie, numero_documento, id_cliente, id_usuario,
                                   total_gravado, total_igv, total_venta))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear venta: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def agregar_detalle_venta(self, id_venta, id_articulo, cantidad, precio_unitario, porcentaje_igv, subtotal):
        """Agrega un artículo al detalle de la venta."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
                    INSERT INTO venta_detalle
                    (id_venta, id_articulo, cantidad, precio_unitario, porcentaje_igv, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s) \
                    """
            cursor.execute(query, (id_venta, id_articulo, cantidad, precio_unitario, porcentaje_igv, subtotal))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al agregar detalle de venta: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def actualizar_stock_venta(self, id_venta, id_almacen):
        """Actualiza el stock basado en la venta."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Obtener el detalle de la venta
            detalle = self.get_detalle_venta(id_venta)
            if not detalle:
                return False

            # Para cada artículo, reducir el stock en el almacén especificado
            for item in detalle:
                # Verificar si existe registro en stock_almacen
                check_query = """
                              SELECT COUNT(*) \
                              FROM stock_almacen
                              WHERE id_articulo = %s \
                                AND id_almacen = %s \
                              """
                cursor.execute(check_query, (item['id_articulo'], id_almacen))

                if cursor.fetchone()[0] > 0:
                    # Actualizar stock existente
                    update_query = """
                                   UPDATE stock_almacen
                                   SET stock_actual = stock_actual - %s
                                   WHERE id_articulo = %s \
                                     AND id_almacen = %s \
                                   """
                    cursor.execute(update_query, (item['cantidad'], item['id_articulo'], id_almacen))
                else:
                    # No se puede vender un artículo que no tiene stock
                    return False

            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al actualizar stock por venta: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def anular_venta(self, id_venta, id_almacen):
        """Anula una venta y revierte el stock."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Revertir el stock
            detalle = self.get_detalle_venta(id_venta)
            for item in detalle:
                update_query = """
                               UPDATE stock_almacen
                               SET stock_actual = stock_actual + %s
                               WHERE id_articulo = %s \
                                 AND id_almacen = %s \
                               """
                cursor.execute(update_query, (item['cantidad'], item['id_articulo'], id_almacen))

            # Marcar la venta como anulada
            anular_query = "UPDATE venta_cabecera SET estado = 'ANULADA' WHERE id_venta = %s"
            cursor.execute(anular_query, (id_venta,))

            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al anular venta: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)