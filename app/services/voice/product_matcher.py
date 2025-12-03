# app/services/voice/product_matcher.py
from app.models.articulo_model import ArticuloModel
from app.models.stock_almacen_model import StockAlmacenModel
from app.database import get_db_connection, close_db_connection
import re
import unicodedata
import nltk
from nltk.stem import SnowballStemmer

# Descargar recursos de NLTK (solo primera vez)
try:
    nltk.data.find('stemmers/snowball_data')
except LookupError:
    nltk.download('snowball_data')


class ProductMatcher:
    def __init__(self):
        self.articulo_model = ArticuloModel()
        self.stock_model = StockAlmacenModel()
        self.stemmer = SnowballStemmer('spanish')

        # Diccionario de sinónimos y variaciones expandido
        self.variaciones = {

            # --- Plurales sin pérdida de significado ---
            'papeles': 'papel',
            'hojas': 'hoja',
            'cuadernos': 'cuaderno',
            'cartulinas': 'cartulina',
            'marcadores': 'marcador',
            'plumones': 'plumon',
            'crayones': 'crayon',
            'plasticinas': 'plasticina',
            'tijeras': 'tijera',
            'gomas': 'goma',
            'reglas': 'regla',

            # --- Variaciones ortográficas o fonéticas reales ---
            'lapices': 'lapiz',
            'colores': 'color',
            'pegamentos': 'pegamento',
            'adhesivos': 'pegamento',
            'scotch': 'cinta',
            'celo': 'cinta',
            'hoja': 'hojas',

            # --- Variaciones de términos según tu inventario ---
            'papelote': 'papelote',  # No debe mezclarse con papel bond
            'bond': 'bond',
            'lustre': 'lustre',
            'sedita': 'sedita',
            'metalico': 'metalico',

            # --- Material escolar común ---
            'marcador acrimax': 'marcador acrimax',
            'plumon acrimax': 'plumon acrimax',
            'plumon pizarra': 'plumon pizarra',
            'marcador pizarra': 'marcador pizarra',

            # --- Términos compuestos comunes reales ---
            'papel lustre': 'papel lustre',
            'papel sedita': 'papel sedita',
            'papel metalico': 'papel metalico',
            'papel bond': 'papel bond',
            'papel a4': 'a4',
            'hoja a4': 'a4',
            'hoja carta': 'carta',
            'hoja oficio': 'oficio',
        }

    def buscar_productos(self, termino_busqueda):
        """
        Busca productos con algoritmo MEJORADO que maneja variaciones
        """
        print(f"🔍 Buscando productos con término: '{termino_busqueda}'")

        # Verificar si es una consulta no relacionada al inventario
        if self._es_consulta_no_relacionada(termino_busqueda):
            return []

        articulos = self.articulo_model.get_articulos_para_voz()

        if not articulos:
            print("⚠️ No se encontraron artículos activos")
            return []

        # NORMALIZACIÓN MEJORADA
        termino_normalizado = self._normalizar_y_mejorar_termino(termino_busqueda)
        palabras_termino = termino_normalizado.split()

        print(f"🔍 Término mejorado: '{termino_normalizado}'")
        print(f"🔍 Palabras a buscar: {palabras_termino}")

        # Solo buscar si hay palabras relevantes
        if not self._tiene_palabras_relevantes(palabras_termino):
            return []

        resultados = []

        # Estrategias de búsqueda con scoring MEJORADO
        for articulo in articulos:
            score = self._calcular_score_relevancia_mejorado(articulo, palabras_termino, termino_normalizado)

            # Umbral más bajo para permitir más resultados
            if score >= 0.3:  # ⬆️ Aumentado umbral ligeramente
                articulo['score_relevancia'] = score
                resultados.append(articulo)

        # Ordenar por relevancia
        resultados.sort(key=lambda x: x['score_relevancia'], reverse=True)

        # Limitar resultados
        resultados = resultados[:10]

        print(f"✅ Resultados válidos: {len(resultados)}")
        for res in resultados[:5]:  # Debug primeros 5
            print(f"   - {res['nombre']} (score: {res['score_relevancia']:.2f})")

        # Enriquecer con stock
        return [self._agregar_informacion_stock(r) for r in resultados]

    def _normalizar_y_mejorar_termino(self, texto):
        """Normaliza texto y aplica mejoras para matching"""
        if not texto:
            return ""

        # 1. Normalización básica
        texto = self._normalizar_texto(texto)

        # 2. Aplicar variaciones conocidas
        for variacion, base in self.variaciones.items():
            if variacion in texto:
                texto = texto.replace(variacion, base)

        # 3. Stemming para raíces comunes
        palabras = texto.split()
        palabras_raiz = [self.stemmer.stem(palabra) for palabra in palabras if len(palabra) > 2]

        return ' '.join(palabras_raiz)

    def _calcular_score_relevancia_mejorado(self, articulo, palabras_termino, termino_completo):
        """Calcula score de relevancia MEJORADO con PRIORIDAD de términos"""
        nombre_normalizado = self._normalizar_texto(articulo['nombre'])
        codigo_normalizado = self._normalizar_texto(articulo['codigo'])
        categoria_normalizada = self._normalizar_texto(articulo.get('categoria_nombre', ''))
        marca_normalizada = self._normalizar_texto(articulo.get('marca_nombre', ''))

        # Aplicar stemming a los textos del artículo también
        nombre_raiz = ' '.join([self.stemmer.stem(p) for p in nombre_normalizado.split()])
        categoria_raiz = ' '.join([self.stemmer.stem(p) for p in categoria_normalizada.split()])

        textos_busqueda = [
            nombre_normalizado, nombre_raiz,
            categoria_normalizada, categoria_raiz,
            codigo_normalizado, marca_normalizada
        ]

        texto_completo = ' '.join(textos_busqueda)
        texto_completo_raiz = ' '.join([self.stemmer.stem(p) for p in texto_completo.split()])

        score = 0.0

        # 🎯 NUEVA ESTRATEGIA: IDENTIFICAR TÉRMINOS CLAVE vs ADJETIVOS
        terminos_clave = self._identificar_terminos_clave(palabras_termino)

        print(f"🔍 Términos clave identificados: {terminos_clave}")

        # ESTRATEGIA 1: Coincidencia exacta del TÉRMINO COMPLETO (máxima prioridad)
        if termino_completo in nombre_normalizado:
            score += 2.0  # ⬆️ Aumentado
            print(f"   ✅ Coincidencia EXACTA del término completo")

        # ESTRATEGIA 2: Coincidencia de TODOS los términos clave (alta prioridad)
        if terminos_clave:
            todos_claves_en_nombre = all(
                any(clave in texto for texto in [nombre_normalizado, nombre_raiz])
                for clave in terminos_clave
            )
            if todos_claves_en_nombre:
                score += 1.5
                print(f"   ✅ Todos los términos clave encontrados: {terminos_clave}")

        # ESTRATEGIA 3: Coincidencia de TÉRMINOS CLAVE individuales
        for termino in terminos_clave:
            raiz_termino = self.stemmer.stem(termino)

            # Alta prioridad si está en NOMBRE
            if termino in nombre_normalizado:
                score += 0.8
            elif raiz_termino in nombre_raiz:
                score += 0.6

            # Media prioridad si está en categoría/marca
            if termino in categoria_normalizada or termino in marca_normalizada:
                score += 0.3

        # ESTRATEGIA 4: Coincidencia de palabras ADJETIVOS (BAJA prioridad)
        palabras_adjetivos = [p for p in palabras_termino if p not in terminos_clave]
        for adjetivo in palabras_adjetivos:
            raiz_adjetivo = self.stemmer.stem(adjetivo)

            # Baja prioridad para adjetivos
            if adjetivo in nombre_normalizado:
                score += 0.2
            elif raiz_adjetivo in nombre_raiz:
                score += 0.1

        # ESTRATEGIA 5: Coincidencia con código (media prioridad)
        if any(palabra in codigo_normalizado for palabra in palabras_termino):
            score += 0.4

        # ESTRATEGIA 6: BONUS por coincidencia exacta de marca/modelo
        if any(palabra in marca_normalizada for palabra in palabras_termino):
            score += 0.3

        # PENALIZACIÓN: Si tiene términos clave pero NO en el nombre
        if terminos_clave:
            claves_faltantes = sum(1 for termino in terminos_clave
                                   if not any(termino in texto for texto in [nombre_normalizado, nombre_raiz]))
            if claves_faltantes > 0:
                score *= 0.3  # ⬇️ Reducir score significativamente
                print(f"   ⚠️ Penalización: faltan {claves_faltantes} términos clave")

        print(f"   📊 Score final: {score:.2f} para: {articulo['nombre']}")
        return min(score, 2.0)  # ⬆️ Aumentado límite por los bonuses

    def _identificar_terminos_clave(self, palabras):
        """Identifica qué palabras son términos clave vs adjetivos"""
        # Palabras que son ADJETIVOS (baja prioridad)
        adjetivos_comunes = {
            'amarillo', 'azul', 'rojo', 'verde', 'negro', 'blanco',
            'grande', 'pequeno', 'mediano', 'fino', 'grueso',
            'brillante', 'opaco', 'transparente', 'fosforescente',
            'claro', 'oscuro', 'pastel', 'fluorescente'
        }

        # Palabras que son TÉRMINOS CLAVE (alta prioridad)
        terminos_clave = []

        for palabra in palabras:
            # Excluir adjetivos comunes y palabras muy cortas
            if (palabra not in adjetivos_comunes and
                    len(palabra) > 2 and
                    not palabra.isdigit()):
                terminos_clave.append(palabra)

        return terminos_clave

    # MANTENER LOS MÉTODOS EXISTENTES (solo mejoramos los de arriba)
    def _normalizar_texto(self, texto):
        """Normaliza texto: minúsculas, sin tildes, sin caracteres especiales"""
        if not texto:
            return ""

        # Convertir a minúsculas
        texto = texto.lower()

        # Remover tildes
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

        # Remover caracteres especiales, mantener letras, números y espacios
        texto = re.sub(r'[^a-z0-9\s]', ' ', texto)

        # Remover espacios extras
        texto = re.sub(r'\s+', ' ', texto).strip()

        return texto

    def _es_consulta_no_relacionada(self, termino):
        """Detecta consultas que no están relacionadas con el inventario"""
        palabras_no_relacionadas = {
            'gato', 'gatos', 'perro', 'perros', 'mascota', 'mascotas',
            'casa', 'casas', 'auto', 'autos', 'carro', 'carros',
            'persona', 'personas', 'amigo', 'amigos', 'familia',
            'comida', 'bebida', 'ropa', 'zapato', 'zapatos',
            'telefono', 'celular', 'computadora', 'laptop'
        }

        termino_normalizado = self._normalizar_texto(termino)
        palabras = set(termino_normalizado.split())

        # Si más del 50% de las palabras son no relacionadas, descartar
        palabras_no_rel = palabras.intersection(palabras_no_relacionadas)
        if len(palabras_no_rel) / max(1, len(palabras)) > 0.5:
            print(f"🚫 Consulta no relacionada detectada: {termino}")
            return True

        return False

    def _tiene_palabras_relevantes(self, palabras):
        """Verifica que haya palabras relevantes para búsqueda de productos"""
        palabras_vacias = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'al', 'a', 'en', 'por', 'para', 'con',
            'que', 'qué', 'cual', 'cuál', 'como', 'cómo',
            'tengo', 'tienes', 'tenemos', 'hay', 'tiene',
            'cuantos', 'cuantas', 'cuanto', 'cuanta'
        }

        palabras_relevantes = [p for p in palabras if p not in palabras_vacias and len(p) > 2]
        return len(palabras_relevantes) > 0

    def _agregar_informacion_stock(self, articulo):
        """Agrega información de stock al artículo - MEJORADO con ambos precios"""
        try:
            if hasattr(self.stock_model, 'get_stock_by_articulo'):
                stock_info = self.stock_model.get_stock_by_articulo(articulo['id_articulo'])
                articulo['stock_actual'] = stock_info.get('stock_total', 0) if stock_info else 0
            else:
                articulo['stock_actual'] = self._obtener_stock_alternativo(articulo['id_articulo'])

            # ✅ NUEVO: Asegurar que ambos precios estén disponibles
            articulo['precio_compra'] = float(articulo.get('precio_compra', 0))
            articulo['precio_venta'] = float(articulo.get('precio_venta', 0))

            articulo['disponible'] = articulo['stock_actual'] > 0
            return articulo

        except Exception as e:
            print(f"⚠️ Error obteniendo stock: {e}")
            articulo['stock_actual'] = 0
            articulo['precio_compra'] = 0
            articulo['precio_venta'] = 0
            articulo['disponible'] = False
            return articulo

    def _obtener_stock_alternativo(self, id_articulo):
        """Método alternativo para obtener stock"""
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
            print(f"Error en método alternativo de stock: {e}")
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            close_db_connection(conn)

    def sugerir_productos_similares(self, termino_no_encontrado):
        """Sugiere productos similares cuando no se encuentra el término"""
        articulos = self.articulo_model.get_articulos_para_voz()
        sugerencias = []

        termino_mejorado = self._normalizar_y_mejorar_termino(termino_no_encontrado)
        palabras_termino = termino_mejorado.split()

        for articulo in articulos:
            nombre_normalizado = self._normalizar_texto(articulo['nombre'])
            nombre_raiz = ' '.join([self.stemmer.stem(p) for p in nombre_normalizado.split()])

            # Buscar coincidencias con raíces
            coincidencias = sum(1 for palabra in palabras_termino
                                if self.stemmer.stem(palabra) in nombre_raiz)

            if coincidencias > 0:
                articulo['score_relevancia'] = coincidencias / len(palabras_termino)
                sugerencias.append(articulo)

            if len(sugerencias) >= 8:  # Más sugerencias
                break

        sugerencias.sort(key=lambda x: x['score_relevancia'], reverse=True)
        return sugerencias