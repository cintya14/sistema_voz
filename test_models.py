# test_correct_model.py
import google.generativeai as genai
from app.config import Config


def test_correct_model():
    config = Config()
    genai.configure(api_key=config.GEMINI_API_KEY)

    print("🔍 Probando modelo CORRECTO...")

    # Modelos de TU lista que SÍ funcionan
    working_models = [
        'models/gemini-2.0-flash',
        'models/gemini-2.0-flash-001',
        'models/gemini-pro-latest',
        'models/gemini-2.0-flash-lite'
    ]

    for model_name in working_models:
        try:
            print(f"\n🧪 Probando: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Responde solo con 'OK'")
            print(f"✅ {model_name} - FUNCIONA: {response.text}")

            # Probar con un comando real
            test_command = "buscar hojas A4"
            response2 = model.generate_content(f"""
            Analiza este comando y devuelve JSON: "{test_command}"
            {{"intencion": "BUSCAR_PRODUCTO", "producto": "hojas A4", "cantidad": null, "confianza": 0.9, "mensaje": "Encontré hojas A4", "necesita_clarificacion": false, "campos_faltantes": []}}
            """)
            print(f"   Comando real: {response2.text[:100]}...")

        except Exception as e:
            print(f"❌ {model_name} - ERROR: {e}")


if __name__ == "__main__":
    test_correct_model()