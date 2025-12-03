// static/voice/voice-config.js
// Configuración centralizada del asistente de voz

export const VOICE_CONFIG = {
    // Palabras de activación
    WAKE_WORDS: [
        'inventario activar',
        'inventario activa',
        'activar inventario',
        'asistente activar',
        'asistente activa',
        'hola inventario',
        'ok inventario'
    ],

    // Umbrales y tiempos
    SIMILARITY_THRESHOLD: 0.8,
    SLEEP_DELAY: 3000,           // ms antes de dormir
    WAKE_TIMEOUT: 500,           // ms para activación
    RETRY_DELAY: 2000,           // ms para reintentar
    RESULT_DISPLAY_TIME: 3000,   // ms mostrando resultados

    // Reconocimiento de voz
    LANGUAGE: 'es-ES',
    MAX_ALTERNATIVES: 1,
    CONTINUOUS: false,
    INTERIM_RESULTS: false,

    // Límites de seguridad
    MAX_COMMAND_LENGTH: 500,
    MAX_RETRIES: 3,

    // Estados del sistema
    STATES: {
        IDLE: 'idle',
        LISTENING_WAKE: 'listening_wake',
        AWAKE: 'awake',
        LISTENING: 'listening',
        PROCESSING: 'processing',
        ERROR: 'error'
    },

    // Colores de intención
    INTENT_COLORS: {
        'BUSCAR_PRODUCTO': 'info',
        'REGISTRAR_ENTRADA': 'success',
        'REGISTRAR_SALIDA': 'warning',
        'DESCONOCIDO': 'secondary',
        'ERROR': 'danger'
    },

    // Mensajes del sistema
    MESSAGES: {
        IDLE: {
            title: 'Sistema en espera',
            detail: 'Di "inventario activar" para comenzar'
        },
        AWAKE: {
            title: 'Asistente activado',
            detail: '¡Dime tu comando!'
        },
        LISTENING: {
            title: 'Grabando audio...',
            detail: 'Habla ahora - el sistema está escuchando'
        },
        PROCESSING: {
            title: 'Procesando comando...',
            detail: 'Analizando tu solicitud'
        }
    },

    // Endpoints API
    API: {
        PROCESS: '/voice/process',
        EXECUTE: '/voice/execute'
    }
};

// Estados válidos y transiciones permitidas
export const STATE_TRANSITIONS = {
    [VOICE_CONFIG.STATES.IDLE]: [
        VOICE_CONFIG.STATES.LISTENING_WAKE,
        VOICE_CONFIG.STATES.AWAKE
    ],
    [VOICE_CONFIG.STATES.LISTENING_WAKE]: [
        VOICE_CONFIG.STATES.AWAKE,
        VOICE_CONFIG.STATES.IDLE
    ],
    [VOICE_CONFIG.STATES.AWAKE]: [
        VOICE_CONFIG.STATES.LISTENING,
        VOICE_CONFIG.STATES.IDLE
    ],
    [VOICE_CONFIG.STATES.LISTENING]: [
        VOICE_CONFIG.STATES.PROCESSING,
        VOICE_CONFIG.STATES.AWAKE,
        VOICE_CONFIG.STATES.ERROR
    ],
    [VOICE_CONFIG.STATES.PROCESSING]: [
        VOICE_CONFIG.STATES.AWAKE,
        VOICE_CONFIG.STATES.IDLE,
        VOICE_CONFIG.STATES.ERROR
    ],
    [VOICE_CONFIG.STATES.ERROR]: [
        VOICE_CONFIG.STATES.IDLE,
        VOICE_CONFIG.STATES.AWAKE
    ]
};