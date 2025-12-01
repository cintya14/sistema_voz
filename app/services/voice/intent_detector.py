# app/services/voice/intent_detector.py
from app.models.voice.voice_model import VoiceModel
from app.services.voice.product_matcher import ProductMatcher


class IntentDetector:
    def __init__(self):
        self.voice_model = VoiceModel()
        self.product_matcher = ProductMatcher()

    def analyze_command(self, text_command):
        """
        Analiza un comando de texto y detecta la intención
        """
        # Primero procesar con Gemini
        gemini_result = self.voice_model.process_command(text_command)

        # Validar y enriquecer el resultado
        validated_result = self._validate_result(gemini_result)

        # Si es una búsqueda, buscar productos reales
        if (validated_result['intencion'] == 'BUSCAR_PRODUCTO' and
                validated_result['producto'] and
                validated_result['confianza'] > 0.3):

            productos_encontrados = self.product_matcher.buscar_productos(validated_result['producto'])

            # Si no hay resultados en la búsqueda principal, usar las sugerencias
            if not productos_encontrados:
                sugerencias = self.product_matcher.sugerir_productos_similares(validated_result['producto'])
                if sugerencias:
                    # Convertir sugerencias en resultados principales
                    productos_encontrados = sugerencias
                    validated_result['mensaje'] = f"🔍 Mostrando sugerencias para '{validated_result['producto']}'"
                    validated_result['es_sugerencia'] = True
                else:
                    validated_result['mensaje'] = f"❌ No encontré productos para '{validated_result['producto']}'"
            else:
                validated_result[
                    'mensaje'] = f"✅ Encontré {len(productos_encontrados)} producto(s) para '{validated_result['producto']}'"
                validated_result['es_sugerencia'] = False

            validated_result['productos_encontrados'] = productos_encontrados
            validated_result['cantidad_resultados'] = len(productos_encontrados)

        # ✅ NUEVO: Procesar movimientos de entrada/salida
        elif validated_result['intencion'] in ['REGISTRAR_ENTRADA', 'REGISTRAR_SALIDA']:
            validated_result = self._procesar_movimiento(validated_result)

        return validated_result

    def _procesar_movimiento(self, result):
        """Procesa un comando de movimiento (entrada/salida)"""
        producto = result.get('producto')
        cantidad = result.get('cantidad')

        if not producto or not cantidad:
            result['necesita_clarificacion'] = True
            campos_faltantes = []
            if not producto:
                campos_faltantes.append('producto')
            if not cantidad:
                campos_faltantes.append('cantidad')
            result['campos_faltantes'] = campos_faltantes
            result['mensaje'] = "Necesito más información para registrar el movimiento"
            return result

        # Buscar el producto
        productos_encontrados = self.product_matcher.buscar_productos(producto)

        if not productos_encontrados:
            result['mensaje'] = f"❌ No encontré el producto '{producto}'"
            result['productos_encontrados'] = []
            return result

        # Si hay múltiples productos, necesitamos clarificación
        if len(productos_encontrados) > 1:
            result['necesita_clarificacion'] = True
            result['campos_faltantes'] = ['producto_especifico']
            result['productos_encontrados'] = productos_encontrados
            result['mensaje'] = f"Encontré varios productos con '{producto}'. ¿Cuál específicamente?"
            return result

        # Un solo producto encontrado
        producto_seleccionado = productos_encontrados[0]
        result['producto_seleccionado'] = producto_seleccionado
        result['productos_encontrados'] = productos_encontrados

        # Para salidas, verificar stock
        if result['intencion'] == 'REGISTRAR_SALIDA':
            stock_actual = producto_seleccionado.get('stock_actual', 0)
            if stock_actual < cantidad:
                result[
                    'mensaje'] = f"❌ Stock insuficiente. Solo hay {stock_actual} unidades de '{producto_seleccionado['nombre']}'"
                result['puede_ejecutar'] = False
                return result

        result['puede_ejecutar'] = True
        result['mensaje'] = self._generar_mensaje_confirmacion(result, producto_seleccionado)

        return result

    def _generar_mensaje_confirmacion(self, result, producto):
        """Genera mensaje de confirmación para el movimiento"""
        tipo = "entrada" if result['intencion'] == 'REGISTRAR_ENTRADA' else "salida"
        return f"✅ ¿Registrar {tipo} de {result['cantidad']} unidades de '{producto['nombre']}'?"

    def _validate_result(self, result):
        """Valida y mejora el resultado de Gemini"""
        # Asegurar que los tipos de datos sean correctos
        if result.get('cantidad'):
            try:
                result['cantidad'] = int(result['cantidad'])
            except (ValueError, TypeError):
                result['cantidad'] = None

        # Validar confianza
        confianza = result.get('confianza', 0)
        if not isinstance(confianza, (int, float)) or confianza < 0:
            result['confianza'] = 0.0
        elif confianza > 1:
            result['confianza'] = 1.0

        # Determinar si necesita clarificación
        if result['intencion'] in ['REGISTRAR_ENTRADA', 'REGISTRAR_SALIDA']:
            if not result['producto'] or not result['cantidad']:
                result['necesita_clarificacion'] = True
                campos_faltantes = []
                if not result['producto']:
                    campos_faltantes.append('producto')
                if not result['cantidad']:
                    campos_faltantes.append('cantidad')
                result['campos_faltantes'] = campos_faltantes

        # Agregar campos adicionales
        result['productos_encontrados'] = []
        result['cantidad_resultados'] = 0
        result['sugerencias'] = []

        return result

    # Agrega este método a la clase IntentDetector
    def _procesar_movimiento(self, result):
        """Procesa un comando de movimiento (entrada/salida) - VERSIÓN MEJORADA"""
        producto = result.get('producto')
        cantidad = result.get('cantidad')

        print(f"🔄 Procesando movimiento: {result['intencion']}, Producto: {producto}, Cantidad: {cantidad}")

        if not producto or not cantidad:
            result['necesita_clarificacion'] = True
            campos_faltantes = []
            if not producto:
                campos_faltantes.append('producto')
            if not cantidad:
                campos_faltantes.append('cantidad')
            result['campos_faltantes'] = campos_faltantes
            result['mensaje'] = "Necesito más información para registrar el movimiento"
            return result

        # Buscar el producto con el nuevo matcher mejorado
        productos_encontrados = self.product_matcher.buscar_productos(producto)

        if not productos_encontrados:
            # Intentar con sugerencias
            sugerencias = self.product_matcher.sugerir_productos_similares(producto)
            if sugerencias:
                result['necesita_clarificacion'] = True
                result['campos_faltantes'] = ['producto_especifico']
                result['productos_encontrados'] = sugerencias
                result['mensaje'] = f"No encontré '{producto}'. ¿Te refieres a alguno de estos?"
            else:
                result['mensaje'] = f"❌ No encontré el producto '{producto}'"
                result['productos_encontrados'] = []
            return result

        # Si hay múltiples productos, necesitamos clarificación
        if len(productos_encontrados) > 1:
            result['necesita_clarificacion'] = True
            result['campos_faltantes'] = ['producto_especifico']
            result['productos_encontrados'] = productos_encontrados
            result['mensaje'] = f"Encontré varios productos. ¿Cuál específicamente?"
            return result

        # Un solo producto encontrado - PREPARAR PARA EJECUCIÓN
        producto_seleccionado = productos_encontrados[0]
        result['producto_seleccionado'] = producto_seleccionado
        result['productos_encontrados'] = productos_encontrados

        # Para salidas, verificar stock
        if result['intencion'] == 'REGISTRAR_SALIDA':
            stock_actual = producto_seleccionado.get('stock_actual', 0)
            if stock_actual < cantidad:
                result[
                    'mensaje'] = f"❌ Stock insuficiente. Solo hay {stock_actual} unidades de '{producto_seleccionado['nombre']}'"
                result['puede_ejecutar'] = False
                return result

        # ✅ MARCAR PARA EJECUCIÓN INMEDIATA cuando hay un solo producto
        result['puede_ejecutar'] = True
        result['listo_para_ejecutar'] = True  # Nueva bandera
        result['mensaje'] = self._generar_mensaje_confirmacion(result, producto_seleccionado)

        print(f"✅ Movimiento listo para ejecutar: {producto_seleccionado['nombre']} x {cantidad}")

        return result