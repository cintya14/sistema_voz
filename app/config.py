import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'sistema_inventarios_voz')

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    VOICE_TIMEOUT_SECONDS = 10
    VOICE_MAX_RETRIES = 3
    VOICE_DEFAULT_ALMACEN = 1
    VOICE_ENABLE_TTS = True
    VOICE_DEFAULT_LANGUAGE = 'es-ES'