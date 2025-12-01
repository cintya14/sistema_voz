import mysql.connector
from app.database import get_db_connection, close_db_connection
from datetime import datetime


class MovimientoModel:
    def __init__(self):
        pass

    def get_all_movimientos(self, tipo=None):
        """Obtiene todos los movimientos, opcionalmente filtrados por tipo."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT mc.*, \
                           tm.nombre      as tipo_movimiento_nombre, \
                           tm.es_entrada, \
                           al.nombre      as almacen_nombre, \
                           u.nombre_usuario, \
                           p.razon_social as proveedor_nombre
                    FROM movimiento_cabecera mc
                             INNER JOIN tipo_movimiento tm ON mc.id_tipo_movimiento = tm.id_tipo_movimiento
                             INNER JOIN almacen al ON mc.id_almacen = al.id_almacen
                             INNER JOIN usuario u ON mc.id_usuario_registro = u.id_usuario
                             LEFT JOIN proveedor p ON mc.id_proveedor = p.id_proveedor \
                    """

            params = []
            if tipo == 'entrada':
                query += " WHERE tm.es_entrada = 1"
            elif tipo == 'salida':
                query += " WHERE tm.es_entrada = 0"

            query += " ORDER BY mc.fecha_movimiento DESC"

            cursor.execute(query, params)
            movimientos = cursor.fetchall()
            return movimientos
        except mysql.connector.Error as err:
            print(f"Error al obtener movimientos: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_movimiento_by_id(self, id_movimiento_cabecera):
        """Obtiene un movimiento por su ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT mc.*, \
                           tm.nombre      as tipo_movimiento_nombre, \
                           tm.es_entrada, \
                           al.nombre      as almacen_nombre, \
                           u.nombre_usuario, \
                           p.razon_social as proveedor_nombre
                    FROM movimiento_cabecera mc
                             INNER JOIN tipo_movimiento tm ON mc.id_tipo_movimiento = tm.id_tipo_movimiento
                             INNER JOIN almacen al ON mc.id_almacen = al.id_almacen
                             INNER JOIN usuario u ON mc.id_usuario_registro = u.id_usuario
                             LEFT JOIN proveedor p ON mc.id_proveedor = p.id_proveedor
                    WHERE mc.id_movimiento_cabecera = %s \
                    """
            cursor.execute(query, (id_movimiento_cabecera,))
            movimiento = cursor.fetchone()
            return movimiento
        except mysql.connector.Error as err:
            print(f"Error al obtener movimiento: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_detalle_movimiento(self, id_movimiento_cabecera):
        """Obtiene el detalle de un movimiento."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                    SELECT md.*, \
                           a.codigo, \
                           a.nombre      as articulo_nombre, \
                           u.nombre      as unidad_nombre, \
                           u.abreviatura as unidad_abreviatura
                    FROM movimiento_detalle md
                             INNER JOIN articulo a ON md.id_articulo = a.id_articulo
                             INNER JOIN unidad_medida u ON a.id_unidad_medida = u.id_unidad_medida
                    WHERE md.id_movimiento_cabecera = %s \
                    """
            cursor.execute(query, (id_movimiento_cabecera,))
            detalle = cursor.fetchall()
            return detalle
        except mysql.connector.Error as err:
            print(f"Error al obtener detalle de movimiento: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def create_movimiento(self, fecha_movimiento, id_almacen, id_tipo_movimiento, observacion, id_usuario,
                          id_proveedor=None):
        """Crea un nuevo movimiento."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = """
                    INSERT INTO movimiento_cabecera
                    (fecha_movimiento, id_almacen, id_tipo_movimiento, observacion, id_usuario_registro, id_proveedor)
                    VALUES (%s, %s, %s, %s, %s, %s) \
                    """
            cursor.execute(query,
                           (fecha_movimiento, id_almacen, id_tipo_movimiento, observacion, id_usuario, id_proveedor))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al crear movimiento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def agregar_detalle_movimiento(self, id_movimiento_cabecera, id_articulo, cantidad, costo_unitario,
                                   precio_venta=None, es_entrada=True):
        """Agrega un detalle al movimiento con ambos precios"""
        conn = get_db_connection()  # ✅ OBTENER CONEXIÓN CORRECTAMENTE
        if conn is None:
            return False

        cursor = conn.cursor()
        try:
            # Determinar precio_venta según el tipo de movimiento
            if precio_venta is None:
                if es_entrada:
                    # Para entradas, precio_venta puede ser igual al costo o NULL
                    precio_venta = costo_unitario
                else:
                    # Para salidas, obtener el precio_venta del artículo
                    articulo = self.get_articulo_by_id(id_articulo)
                    precio_venta = articulo['precio_venta'] if articulo else costo_unitario

            query = """
                INSERT INTO movimiento_detalle 
                (id_movimiento_cabecera, id_articulo, cantidad, costo_unitario, precio_venta)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_movimiento_cabecera, id_articulo, cantidad, costo_unitario, precio_venta))
            conn.commit()  # ✅ USAR conn EN LUGAR DE self.conn
            print(
                f"✅ Detalle guardado: Movimiento {id_movimiento_cabecera}, Artículo {id_articulo}, Cantidad {cantidad}")
            return True
        except Exception as e:
            print(f"❌ Error al agregar detalle: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)  # ✅ CERRAR CONEXIÓN

    def actualizar_stock(self, id_movimiento_cabecera):
        """Actualiza el stock basado en el movimiento."""
        print(f"DEBUG: Iniciando actualizar_stock para movimiento {id_movimiento_cabecera}")

        conn = get_db_connection()
        if conn is None:
            print("DEBUG: Error de conexión a la base de datos")
            return False

        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            print("DEBUG: Transacción iniciada")

            # Obtener información del movimiento
            movimiento = self.get_movimiento_by_id(id_movimiento_cabecera)
            if not movimiento:
                print("DEBUG: Movimiento no encontrado")
                conn.rollback()
                return False

            print(f"DEBUG: Movimiento encontrado - Tipo: {'ENTRADA' if movimiento['es_entrada'] else 'SALIDA'}")
            print(f"DEBUG: Almacén: {movimiento['id_almacen']}")

            # Obtener el detalle del movimiento
            detalle = self.get_detalle_movimiento(id_movimiento_cabecera)
            if not detalle:
                print("DEBUG: No hay detalle del movimiento")
                conn.rollback()
                return False

            print(f"DEBUG: {len(detalle)} artículos en el detalle")

            # Actualizar stock para cada artículo
            for item in detalle:
                print(f"DEBUG: Procesando artículo {item['id_articulo']} - Cantidad: {item['cantidad']}")

                # Verificar si existe registro en stock_almacen
                check_query = """
                              SELECT stock_actual
                              FROM stock_almacen
                              WHERE id_articulo = %s \
                                AND id_almacen = %s \
                              """
                cursor.execute(check_query, (item['id_articulo'], movimiento['id_almacen']))
                resultado = cursor.fetchone()

                if resultado:
                    stock_actual = resultado['stock_actual']
                    print(f"DEBUG: Stock actual encontrado: {stock_actual}")

                    if movimiento['es_entrada']:
                        nuevo_stock = stock_actual + item['cantidad']
                        update_query = """
                                       UPDATE stock_almacen
                                       SET stock_actual = %s
                                       WHERE id_articulo = %s \
                                         AND id_almacen = %s \
                                       """
                        print(f"DEBUG: Entrada - Nuevo stock: {nuevo_stock}")
                        cursor.execute(update_query, (nuevo_stock, item['id_articulo'], movimiento['id_almacen']))
                    else:
                        # Verificar stock suficiente para salidas
                        if stock_actual < item['cantidad']:
                            print(
                                f"DEBUG: ERROR - Stock insuficiente. Actual: {stock_actual}, Requerido: {item['cantidad']}")
                            conn.rollback()
                            return False
                        nuevo_stock = stock_actual - item['cantidad']
                        update_query = """
                                       UPDATE stock_almacen
                                       SET stock_actual = %s
                                       WHERE id_articulo = %s \
                                         AND id_almacen = %s \
                                       """
                        print(f"DEBUG: Salida - Nuevo stock: {nuevo_stock}")
                        cursor.execute(update_query, (nuevo_stock, item['id_articulo'], movimiento['id_almacen']))

                    print(f"DEBUG: Stock actualizado para artículo {item['id_articulo']}")

                else:
                    print(f"DEBUG: No existe registro en stock_almacen para artículo {item['id_articulo']}")

                    # Insertar nuevo registro (solo para entradas)
                    if movimiento['es_entrada']:
                        insert_query = """
                                       INSERT INTO stock_almacen (id_articulo, id_almacen, stock_actual)
                                       VALUES (%s, %s, %s) \
                                       """
                        cursor.execute(insert_query, (item['id_articulo'], movimiento['id_almacen'], item['cantidad']))
                        print(f"DEBUG: Nuevo registro creado para artículo {item['id_articulo']}")
                    else:
                        # No se puede crear stock negativo
                        print(f"DEBUG: ERROR - No se puede crear stock negativo para salida")
                        conn.rollback()
                        return False

            print("DEBUG: Todos los artículos procesados - registrando en kardex")

            # REGISTRAR EN KARDEX DESPUÉS DE ACTUALIZAR STOCK
            if not self.registrar_kardex(id_movimiento_cabecera):
                print("DEBUG: ERROR - No se pudo registrar en kardex")
                conn.rollback()
                return False

            print("DEBUG: Transacción confirmada - stock y kardex actualizados exitosamente")
            conn.commit()
            return True

        except mysql.connector.Error as err:
            print(f"DEBUG: Error en la base de datos: {err}")
            conn.rollback()
            return False
        except Exception as e:
            print(f"DEBUG: Error general: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)
            print("DEBUG: Conexión cerrada")



    def verificar_stock_suficiente(self, id_movimiento_cabecera):
        """Verifica si hay stock suficiente para un movimiento de salida."""
        print(f"DEBUG: Verificando stock para movimiento {id_movimiento_cabecera}")

        conn = get_db_connection()
        if conn is None:
            return False

        cursor = conn.cursor(dictionary=True)
        try:
            # Obtener información del movimiento
            movimiento = self.get_movimiento_by_id(id_movimiento_cabecera)
            if not movimiento:
                print("DEBUG: Movimiento no encontrado")
                return False

            # Si es entrada, no necesita verificación de stock
            if movimiento['es_entrada']:
                print("DEBUG: Es entrada - no necesita verificación de stock")
                return True

            print(f"DEBUG: Es salida - verificando stock...")

            # Obtener el detalle del movimiento
            detalle = self.get_detalle_movimiento(id_movimiento_cabecera)

            for item in detalle:
                print(f"DEBUG: Verificando artículo {item['id_articulo']} - cantidad: {item['cantidad']}")

                # Verificar stock actual
                check_query = """
                              SELECT stock_actual
                              FROM stock_almacen
                              WHERE id_articulo = %s \
                                AND id_almacen = %s \
                              """
                cursor.execute(check_query, (item['id_articulo'], movimiento['id_almacen']))
                resultado = cursor.fetchone()

                if not resultado:
                    print(f"DEBUG: ERROR - No existe stock para artículo {item['id_articulo']}")
                    return False

                stock_actual = resultado['stock_actual']
                print(f"DEBUG: Stock actual: {stock_actual}, requerido: {item['cantidad']}")

                if stock_actual < item['cantidad']:
                    print(f"DEBUG: ERROR - Stock insuficiente. Actual: {stock_actual}, Requerido: {item['cantidad']}")
                    return False

            print("DEBUG: Stock suficiente para todos los artículos")
            return True

        except Exception as e:
            print(f"DEBUG: Error al verificar stock: {e}")
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_movimiento(self, id_movimiento_cabecera):
        """Elimina un movimiento y su detalle."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Primero eliminar el detalle
            delete_detalle_query = "DELETE FROM movimiento_detalle WHERE id_movimiento_cabecera = %s"
            cursor.execute(delete_detalle_query, (id_movimiento_cabecera,))

            # Luego eliminar la cabecera
            delete_cabecera_query = "DELETE FROM movimiento_cabecera WHERE id_movimiento_cabecera = %s"
            cursor.execute(delete_cabecera_query, (id_movimiento_cabecera,))

            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al eliminar movimiento: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def registrar_kardex(self, id_movimiento_cabecera):
        """Registra el movimiento en el kardex."""
        print(f"DEBUG: Registrando kardex para movimiento {id_movimiento_cabecera}")

        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            conn.start_transaction()

            # Obtener información del movimiento
            movimiento = self.get_movimiento_by_id(id_movimiento_cabecera)
            detalle = self.get_detalle_movimiento(id_movimiento_cabecera)

            if not movimiento or not detalle:
                print("DEBUG: No se pudo obtener movimiento o detalle para kardex")
                conn.rollback()
                return False

            print(f"DEBUG: Registrando kardex para {len(detalle)} artículos")

            # Para cada artículo en el detalle, registrar en kardex
            for item in detalle:
                print(f"DEBUG: Procesando kardex para artículo {item['id_articulo']}")

                # Obtener el último saldo del artículo en este almacén
                saldo_query = """
                              SELECT cantidad_saldo, costo_promedio, valor_saldo
                              FROM kardex
                              WHERE id_articulo = %s \
                                AND id_almacen = %s
                              ORDER BY fecha DESC, id_kardex DESC LIMIT 1 \
                              """
                cursor.execute(saldo_query, (item['id_articulo'], movimiento['id_almacen']))
                saldo_anterior = cursor.fetchone()

                if saldo_anterior:
                    cantidad_saldo_anterior = saldo_anterior[0] if saldo_anterior[0] is not None else 0
                    costo_promedio_anterior = saldo_anterior[1] if saldo_anterior[1] is not None else 0
                    valor_saldo_anterior = saldo_anterior[2] if saldo_anterior[2] is not None else 0
                else:
                    cantidad_saldo_anterior = 0
                    costo_promedio_anterior = 0
                    valor_saldo_anterior = 0

                print(f"DEBUG: Saldo anterior - Cantidad: {cantidad_saldo_anterior}, Costo: {costo_promedio_anterior}")

                # Calcular nuevos valores según tipo de movimiento
                if movimiento['es_entrada']:
                    cantidad_entrada = item['cantidad']
                    cantidad_salida = 0
                    costo_entrada = item['costo_unitario']
                    costo_salida = 0

                    # Calcular nuevo costo promedio (solo para entradas)
                    if cantidad_saldo_anterior + cantidad_entrada > 0:
                        nuevo_costo_promedio = (
                                                       (cantidad_saldo_anterior * costo_promedio_anterior) +
                                                       (cantidad_entrada * costo_entrada)
                                               ) / (cantidad_saldo_anterior + cantidad_entrada)
                    else:
                        nuevo_costo_promedio = costo_entrada

                    print(f"DEBUG: Entrada - Nuevo costo promedio: {nuevo_costo_promedio}")
                else:
                    cantidad_entrada = 0
                    cantidad_salida = item['cantidad']
                    costo_entrada = 0
                    costo_salida = costo_promedio_anterior  # Para salidas, usamos el costo promedio
                    nuevo_costo_promedio = costo_promedio_anterior
                    print(f"DEBUG: Salida - Costo salida: {costo_salida}")

                # Calcular nuevo saldo
                nuevo_saldo = cantidad_saldo_anterior + cantidad_entrada - cantidad_salida
                valor_saldo = nuevo_saldo * nuevo_costo_promedio

                print(f"DEBUG: Nuevos valores - Saldo: {nuevo_saldo}, Valor: {valor_saldo}")

                # Generar referencia de documento
                tipo_documento_ref = movimiento['tipo_movimiento_nombre']
                numero_documento_ref = f"MOV-{movimiento['id_movimiento_cabecera']}"

                # Insertar en kardex
                kardex_query = """
                               INSERT INTO kardex
                               (fecha, id_almacen, id_articulo, id_tipo_movimiento,
                                tipo_documento, numero_documento,
                                cantidad_entrada, costo_entrada, cantidad_salida, costo_salida,
                                cantidad_saldo, costo_promedio, valor_saldo)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                               """
                cursor.execute(kardex_query, (
                    movimiento['fecha_movimiento'],
                    movimiento['id_almacen'],
                    item['id_articulo'],
                    movimiento['id_tipo_movimiento'],
                    tipo_documento_ref,
                    numero_documento_ref,
                    cantidad_entrada,
                    costo_entrada,
                    cantidad_salida,
                    costo_salida,
                    nuevo_saldo,
                    nuevo_costo_promedio,
                    valor_saldo
                ))

                print(f"DEBUG: Kardex registrado para artículo {item['id_articulo']}")

            conn.commit()
            print("DEBUG: Kardex registrado exitosamente")
            return True

        except mysql.connector.Error as err:
            print(f"DEBUG: Error al registrar en kardex: {err}")
            conn.rollback()
            return False
        except Exception as e:
            print(f"DEBUG: Error general en kardex: {e}")
            conn.rollback()
            return False
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
            query = "SELECT * FROM articulo WHERE id_articulo = %s"
            cursor.execute(query, (id_articulo,))
            articulo = cursor.fetchone()
            return articulo
        except mysql.connector.Error as err:
            print(f"Error al obtener artículo: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

