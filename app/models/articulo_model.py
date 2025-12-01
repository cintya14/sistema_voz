import mysql.connector
from app.database import get_db_connection, close_db_connection

class ArticuloModel:
    def __init__(self):
        pass

    def get_all_articulos(self):
        """Obtiene todos los artículos de la tabla 'articulo'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT a.*, c.nombre as categoria_nombre, m.nombre as marca_nombre, 
                   u.nombre as unidad_nombre, u.abreviatura as unidad_abreviatura
            FROM articulo a
            LEFT JOIN categoria c ON a.id_categoria = c.id_categoria
            LEFT JOIN marca m ON a.id_marca = m.id_marca
            LEFT JOIN unidad_medida u ON a.id_unidad_medida = u.id_unidad_medida
            ORDER BY a.nombre
            """
            cursor.execute(query)
            articulos = cursor.fetchall()
            return articulos
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los artículos: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_articulo_by_id(self, id_articulo):
        """Obtiene un artículo por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT a.*, c.nombre as categoria_nombre, m.nombre as marca_nombre,
                   u.nombre as unidad_nombre, u.abreviatura as unidad_abreviatura
            FROM articulo a
            LEFT JOIN categoria c ON a.id_categoria = c.id_categoria
            LEFT JOIN marca m ON a.id_marca = m.id_marca
            LEFT JOIN unidad_medida u ON a.id_unidad_medida = u.id_unidad_medida
            WHERE a.id_articulo = %s
            """
            cursor.execute(query, (id_articulo,))
            articulo = cursor.fetchone()
            return articulo
        except mysql.connector.Error as err:
            print(f"Error al obtener artículo por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_articulo(self, codigo, nombre, precio_compra, precio_venta, stock_minimo,
                       id_categoria, id_marca, id_unidad_medida):
        """Crea un nuevo artículo en la tabla 'articulo'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación simple para evitar artículos duplicados por código
            check_query = "SELECT COUNT(*) FROM articulo WHERE codigo = %s"
            cursor.execute(check_query, (codigo,))
            if cursor.fetchone()[0] > 0:
                print("Error: El código del artículo ya existe.")
                return False

            query = """
            INSERT INTO articulo (codigo, nombre, precio_compra, precio_venta, stock_minimo,
                                id_categoria, id_marca, id_unidad_medida)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (codigo, nombre, precio_compra, precio_venta, stock_minimo,
                                 id_categoria, id_marca, id_unidad_medida))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear artículo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_articulo(self, id_articulo, codigo, nombre, precio_compra, precio_venta,
                       stock_minimo, id_categoria, id_marca, id_unidad_medida):
        """Actualiza un artículo existente en la tabla 'articulo'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Validación para evitar duplicados en el código (excluyendo el artículo actual)
            check_query = "SELECT COUNT(*) FROM articulo WHERE codigo = %s AND id_articulo != %s"
            cursor.execute(check_query, (codigo, id_articulo))
            if cursor.fetchone()[0] > 0:
                print("Error: El código del artículo ya existe en otro registro.")
                return False

            query = """
            UPDATE articulo 
            SET codigo = %s, nombre = %s, precio_compra = %s, precio_venta = %s, 
                stock_minimo = %s, id_categoria = %s, id_marca = %s, id_unidad_medida = %s
            WHERE id_articulo = %s
            """
            cursor.execute(query, (codigo, nombre, precio_compra, precio_venta, stock_minimo,
                                 id_categoria, id_marca, id_unidad_medida, id_articulo))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar artículo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_articulo(self, id_articulo):
        """Elimina un artículo de la tabla 'articulo'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # NOTA: En un sistema de inventario real, debes verificar
            # la integridad referencial (ej: si hay movimientos con este artículo).
            query = "DELETE FROM articulo WHERE id_articulo = %s"
            cursor.execute(query, (id_articulo,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar artículo: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    # En tu ArticuloModel, agrega este método específico para voz:


    def get_articulos_para_voz(self):
        """Obtiene artículos con todos los campos necesarios para el asistente de voz"""
        conn = get_db_connection()
        if conn is None:
            return []

        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT a.id_articulo, \
                           a.codigo, \
                           a.nombre, \
                           a.precio_compra, \
                           a.precio_venta, \
                           a.stock_minimo, \
                           a.estado, \
                           c.nombre       as categoria_nombre, \
                           m.nombre       as marca_nombre, \
                           um.nombre      as unidad_medida_nombre, \
                           um.abreviatura as unidad_abreviatura
                    -- REMOVED: a.descripcion porque no existe en tu tabla
                    FROM articulo a
                             LEFT JOIN categoria c ON a.id_categoria = c.id_categoria
                             LEFT JOIN marca m ON a.id_marca = m.id_marca
                             LEFT JOIN unidad_medida um ON a.id_unidad_medida = um.id_unidad_medida
                    WHERE a.estado = 'ACTIVO'
                    ORDER BY a.nombre \
                    """
            cursor.execute(query)
            articulos = cursor.fetchall()

            # Asegurar que todos los campos existan
            for articulo in articulos:
                articulo.setdefault('categoria_nombre', '')
                articulo.setdefault('marca_nombre', '')
                articulo.setdefault('unidad_medida_nombre', '')

            return articulos

        except Exception as e:
            print(f"Error al obtener artículos para voz: {e}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)
