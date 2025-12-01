# app/services/voice/movement_service.py
from app.models.movimiento_model import MovimientoModel
from app.models.articulo_model import ArticuloModel
from app.models.almacen_model import AlmacenModel
from app.database import get_db_connection, close_db_connection
from datetime import datetime


class MovementService:
    def __init__(self):
        self.movimiento_model = MovimientoModel()
        self.articulo_model = ArticuloModel()
        self.almacen_model = AlmacenModel()

    def registrar_entrada(self, id_articulo, cantidad, id_usuario, observaciones=None):
        """Registra una entrada de producto - ACTUALIZADO CON PRECIO_VENTA"""
        try:
            print(f"🎯 [MOVEMENT] Confirmando entrada: Artículo {id_articulo}, Cantidad {cantidad}")

            # ✅ PRIMERO: Validar que el artículo existe
            articulo = self.articulo_model.get_articulo_by_id(id_articulo)
            if not articulo:
                return False, "Artículo no encontrado"

            # ✅ SEGUNDO: Obtener información necesaria
            almacenes = self.almacen_model.get_all_almacenes()
            id_almacen = almacenes[0]['id_almacen'] if almacenes else 1
            costo_unitario = articulo['precio_compra']

            # ✅ NUEVO: Para entradas, precio_venta = costo_unitario
            precio_venta = costo_unitario

            print(f"🎯 [MOVEMENT] Creando movimiento de ENTRADA...")

            # ✅ TERCERO: Crear movimiento
            movimiento_id = self.movimiento_model.create_movimiento(
                fecha_movimiento=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                id_almacen=id_almacen,
                id_tipo_movimiento=1,  # COMPRA
                observacion=observaciones or f"Entrada por voz: {cantidad} unidades de {articulo['nombre']}",
                id_usuario=id_usuario
            )

            if not movimiento_id:
                return False, "Error al crear movimiento"

            # ✅ ACTUALIZADO: Agregar detalle CON PRECIO_VENTA
            success = self.movimiento_model.agregar_detalle_movimiento(
                id_movimiento_cabecera=movimiento_id,
                id_articulo=id_articulo,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                precio_venta=precio_venta,  # ✅ NUEVO PARÁMETRO
                es_entrada=True  # ✅ NUEVO PARÁMETRO
            )

            if not success:
                return False, "Error al agregar detalle"

            # ✅ CUARTO: Actualizar stock
            if self.movimiento_model.actualizar_stock(movimiento_id):
                print(f"✅ [MOVEMENT] Entrada registrada exitosamente: {cantidad} unidades de {articulo['nombre']}")
                return True, f"✅ Entrada registrada: {cantidad} unidades de {articulo['nombre']}"
            else:
                return False, "Error al actualizar stock"

        except Exception as e:
            print(f"❌ [MOVEMENT] Error registrando entrada: {e}")
            return False, f"Error del sistema: {str(e)}"

    def registrar_salida(self, id_articulo, cantidad, id_usuario, observaciones=None):
        """Registra una salida de producto - ACTUALIZADO CON PRECIO_VENTA"""
        try:
            print(f"🎯 [MOVEMENT] Confirmando salida: Artículo {id_articulo}, Cantidad {cantidad}")

            # ✅ PRIMERO: Validar que el artículo existe
            articulo = self.articulo_model.get_articulo_by_id(id_articulo)
            if not articulo:
                return False, "Artículo no encontrado"

            # ✅ VERIFICAR STOCK ANTES de crear movimiento
            stock_actual = self._obtener_stock_actual(id_articulo)
            if stock_actual < cantidad:
                return False, f"❌ Stock insuficiente. Solo hay {stock_actual} unidades de '{articulo['nombre']}'"

            # ✅ SEGUNDO: Obtener información necesaria
            almacenes = self.almacen_model.get_all_almacenes()
            id_almacen = almacenes[0]['id_almacen'] if almacenes else 1
            costo_unitario = articulo['precio_compra']

            # ✅ NUEVO: Para salidas, usar precio_venta real del artículo
            precio_venta = articulo['precio_venta']

            print(f"🎯 [MOVEMENT] Creando movimiento de SALIDA...")

            # ✅ TERCERO: Crear movimiento
            movimiento_id = self.movimiento_model.create_movimiento(
                fecha_movimiento=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                id_almacen=id_almacen,
                id_tipo_movimiento=6,  # VENTA
                observacion=observaciones or f"Salida por voz: {cantidad} unidades de {articulo['nombre']}",
                id_usuario=id_usuario
            )

            if not movimiento_id:
                return False, "Error al crear movimiento"

            # ✅ ACTUALIZADO: Agregar detalle CON PRECIO_VENTA
            success = self.movimiento_model.agregar_detalle_movimiento(
                id_movimiento_cabecera=movimiento_id,
                id_articulo=id_articulo,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                precio_venta=precio_venta,  # ✅ NUEVO PARÁMETRO
                es_entrada=False  # ✅ NUEVO PARÁMETRO
            )

            if not success:
                return False, "Error al agregar detalle"

            # ✅ CUARTO: Actualizar stock
            if self.movimiento_model.actualizar_stock(movimiento_id):
                # ✅ NUEVO: Calcular total de venta
                total_venta = cantidad * precio_venta
                print(f"✅ [MOVEMENT] Salida registrada exitosamente: {cantidad} unidades de {articulo['nombre']}")
                return True, f"✅ Venta registrada: {cantidad} unidades de {articulo['nombre']} - Total: S/ {total_venta:.2f}"
            else:
                return False, "Error al actualizar stock"

        except Exception as e:
            print(f"❌ [MOVEMENT] Error registrando salida: {e}")
            return False, f"Error del sistema: {str(e)}"

    def _obtener_stock_actual(self, id_articulo):
        """Obtiene el stock actual de un artículo"""
        try:
            conn = get_db_connection()
            if conn is None:
                return 0

            cursor = conn.cursor(dictionary=True)
            query = "SELECT COALESCE(SUM(stock_actual), 0) as stock FROM stock_almacen WHERE id_articulo = %s"
            cursor.execute(query, (id_articulo,))
            result = cursor.fetchone()
            return result['stock'] if result else 0
        except Exception as e:
            print(f"Error obteniendo stock: {e}")
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            close_db_connection(conn)

    # ✅ ACTUALIZADO: Método para validar movimiento sin ejecutarlo
    def validar_movimiento(self, id_articulo, cantidad, tipo_movimiento):
        """Valida si un movimiento es posible sin ejecutarlo"""
        try:
            articulo = self.articulo_model.get_articulo_by_id(id_articulo)
            if not articulo:
                return False, "Artículo no encontrado"

            if tipo_movimiento == 'REGISTRAR_SALIDA':
                stock_actual = self._obtener_stock_actual(id_articulo)
                if stock_actual < cantidad:
                    return False, f"Stock insuficiente. Solo hay {stock_actual} unidades"

            return True, "Movimiento válido"
        except Exception as e:
            return False, f"Error validando movimiento: {str(e)}"