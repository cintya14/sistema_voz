import mysql.connector
from app.database import get_db_connection, close_db_connection
from datetime import datetime

class ConteoFisicoModel:
    def __init__(self):
        pass

    def get_all_conteos(self):
        """Obtiene todos los conteos físicos."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                cc.*,
                al.nombre as almacen_nombre,
                u.nombre_usuario
            FROM conteo_inventario_cabecera cc
            INNER JOIN almacen al ON cc.id_almacen = al.id_almacen
            INNER JOIN usuario u ON cc.id_usuario_responsable = u.id_usuario
            ORDER BY cc.fecha_inicio DESC
            """
            cursor.execute(query)
            conteos = cursor.fetchall()
            return conteos
        except mysql.connector.Error as err:
            print(f"Error al obtener conteos: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_conteo_by_id(self, id_conteo):
        """Obtiene un conteo por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                cc.*,
                al.nombre as almacen_nombre,
                u.nombre_usuario
            FROM conteo_inventario_cabecera cc
            INNER JOIN almacen al ON cc.id_almacen = al.id_almacen
            INNER JOIN usuario u ON cc.id_usuario_responsable = u.id_usuario
            WHERE cc.id_conteo = %s
            """
            cursor.execute(query, (id_conteo,))
            conteo = cursor.fetchone()
            return conteo
        except mysql.connector.Error as err:
            print(f"Error al obtener conteo: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_detalle_conteo(self, id_conteo):
        """Obtiene el detalle de un conteo."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                cd.*,
                a.codigo,
                a.nombre as articulo_nombre,
                a.precio_compra
            FROM conteo_inventario_detalle cd
            INNER JOIN articulo a ON cd.id_articulo = a.id_articulo
            WHERE cd.id_conteo = %s
            """
            cursor.execute(query, (id_conteo,))
            detalle = cursor.fetchall()
            return detalle
        except mysql.connector.Error as err:
            print(f"Error al obtener detalle de conteo: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_conteo(self, fecha_inicio, id_almacen, id_usuario, observaciones):
        """Crea un nuevo conteo."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO conteo_inventario_cabecera 
            (fecha_inicio, id_almacen, id_usuario_responsable, observaciones)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (fecha_inicio, id_almacen, id_usuario, observaciones))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear conteo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def agregar_detalle_conteo(self, id_conteo, id_articulo, stock_sistema, stock_contado):
        """Agrega un artículo al detalle del conteo."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Calcular diferencia
            diferencia = stock_contado - stock_sistema

            query = """
            INSERT INTO conteo_inventario_detalle 
            (id_conteo, id_articulo, stock_sistema_al_contar, stock_contado, diferencia)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_conteo, id_articulo, stock_sistema, stock_contado, diferencia))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al agregar detalle de conteo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def finalizar_conteo(self, id_conteo, fecha_fin):
        """Finaliza un conteo."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
            UPDATE conteo_inventario_cabecera 
            SET fecha_fin = %s, estado = 'FINALIZADO'
            WHERE id_conteo = %s
            """
            cursor.execute(query, (fecha_fin, id_conteo))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al finalizar conteo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def ajustar_stock(self, id_conteo):
        """Ajusta el stock basado en el conteo."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Obtener el detalle del conteo
            detalle = self.get_detalle_conteo(id_conteo)
            if not detalle:
                return False

            # Obtener el almacén del conteo
            conteo = self.get_conteo_by_id(id_conteo)
            id_almacen = conteo['id_almacen']

            # Actualizar el stock por cada artículo
            for item in detalle:
                update_query = """
                UPDATE stock_almacen 
                SET stock_actual = %s 
                WHERE id_articulo = %s AND id_almacen = %s
                """
                cursor.execute(update_query, (item['stock_contado'], item['id_articulo'], id_almacen))

            # Marcar el conteo como ajustado
            update_conteo_query = "UPDATE conteo_inventario_cabecera SET estado = 'AJUSTADO' WHERE id_conteo = %s"
            cursor.execute(update_conteo_query, (id_conteo,))

            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al ajustar stock: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)