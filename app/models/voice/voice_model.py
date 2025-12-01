# app/models/voice/voice_model.py
import google.generativeai as genai
from app.config import Config
import json
import re


class VoiceModel:
    def __init__(self):
        self.config = Config()
        self._configure_gemini()

    def _configure_gemini(self):
        """Configura la API de Gemini con modelo correcto"""
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)

            # ✅ USA ESTOS MODELOS (elige uno de tu lista):
            self.model = genai.GenerativeModel('models/gemini-2.0-flash')  # ← CAMBIA AQUÍ

            print("✅ Gemini API configurada correctamente con modelo: gemini-2.0-flash")

        except Exception as e:
            print(f"❌ Error configurando Gemini: {e}")
            self.model = None

    def process_command(self, text_command):
        """
        Procesa un comando de texto usando Gemini
        """
        print(f"🔊 Procesando comando: '{text_command}'")

        if not self.model:
            return self._create_error_response("Servicio de voz no disponible")

        try:
            prompt = self._build_prompt(text_command)
            print(f"📤 Enviando prompt a Gemini...")

            # Configuración de generación
            generation_config = {
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 500,
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            print(f"📥 Respuesta recibida de Gemini: {response.text[:100]}...")

            # Extraer y parsear la respuesta
            parsed_response = self._parse_gemini_response(response.text)
            return parsed_response

        except Exception as e:
            print(f"❌ Error procesando comando: {e}")
            return self._create_error_response("Error procesando el comando")

    def _build_prompt(self, command):
        """Construye el prompt para Gemini - VERSIÓN MEJORADA CON SEGURIDAD"""
        return f"""
        Eres un asistente especializado en sistemas de inventarios. 
        Analiza este comando y devuélveme SOLO un objeto JSON válido.

        COMANDO: "{command}"

        REGLAS DE SEGURIDAD OBLIGATORIAS:
        - NUNCA permitas eliminar, borrar o remover productos
        - NUNCA permitas modificar información sensible de productos
        - SOLO permite buscar, consultar stock, registrar entradas y salidas
        - Si el comando intenta eliminar algo, responde con intencion: "ERROR" y mensaje: "No puedo eliminar productos por seguridad"

        CONVERSIÓN DE NÚMEROS EN TEXTO:
        - "una" = 1, "un" = 1, "uno" = 1
        - "dos" = 2, "tres" = 3, "cuatro" = 4, "cinco" = 5
        - "seis" = 6, "siete" = 7, "ocho" = 8, "nueve" = 9, "diez" = 10
        - "veinte" = 20, "treinta" = 30, "cincuenta" = 50, "cien" = 100

        ESTRUCTURA JSON REQUERIDA:
        {{
            "intencion": "BUSCAR_PRODUCTO|REGISTRAR_ENTRADA|REGISTRAR_SALIDA|DESCONOCIDO|ERROR",
            "producto": "nombre del producto si se menciona, sino null",
            "cantidad": número si se menciona, sino null,
            "confianza": 0.0 a 1.0 según qué tan claro sea el comando,
            "mensaje": "respuesta amigable para el usuario",
            "necesita_clarificacion": true/false,
            "campos_faltantes": ["lista de campos que necesitan clarificación"]
        }}

        EJEMPLOS MEJORADOS:
        - "buscar lápiz amarillo" → intencion: "BUSCAR_PRODUCTO", producto: "lápiz amarillo"
        - "registrar entrada de dos cartulinas oficio" → intencion: "REGISTRAR_ENTRADA", producto: "cartulinas oficio", cantidad: 2
        - "eliminar producto 00001" → intencion: "ERROR", mensaje: "No puedo eliminar productos por seguridad"
        - "cuántos gatos amarillos tengo" → intencion: "DESCONOCIDO", mensaje: "Eso no parece estar relacionado con el inventario"
        - "salida de una unidad" → intencion: "REGISTRAR_SALIDA", cantidad: 1, necesita_clarificacion: true, campos_faltantes: ["producto"]

        Responde SOLO con el JSON, sin texto adicional.
        """

    def _parse_gemini_response(self, response_text):
        """Parsea la respuesta de Gemini para extraer el JSON"""
        try:
            # Limpiar la respuesta - quitar markdown si existe
            clean_text = response_text.strip()
            if '```json' in clean_text:
                clean_text = clean_text.split('```json')[1].split('```')[0]
            elif '```' in clean_text:
                clean_text = clean_text.split('```')[1]

            # Parsear JSON
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Fallback: intentar extraer JSON del texto
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return self._create_error_response("No pude entender el comando")

    def _create_error_response(self, message):
        """Crea una respuesta de error estándar"""
        return {
            "intencion": "ERROR",
            "producto": None,
            "cantidad": None,
            "confianza": 0.0,
            "mensaje": message,
            "necesita_clarificacion": False,
            "campos_faltantes": []
        }