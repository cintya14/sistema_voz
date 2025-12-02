# config.py

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui' # ¡Cambia esto por una clave segura!
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '' # Tu contraseña de MySQL
    MYSQL_DB = 'sistema_inventarios_voz'

    # CONFIGURACIÓN DE VOZ - AGREGAR ESTO
    GEMINI_API_KEY = 'AIzaSyALEMRbFGr9vxGsDyUc73V6agEh9R4ANlo'  # Obtén una API key de Google Gemini
    VOICE_TIMEOUT_SECONDS = 10
    VOICE_MAX_RETRIES = 3
    VOICE_DEFAULT_ALMACEN = 1  # ID del almacén principal
    VOICE_ENABLE_TTS = True
    VOICE_DEFAULT_LANGUAGE = 'es-ES'