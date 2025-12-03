// static/voice/voice-utils.js
// Utilidades y funciones auxiliares

export class VoiceUtils {
    /**
     * Sanitiza el input del usuario
     */
    static sanitizeInput(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        return text.trim().slice(0, 500);
    }

    /**
     * Calcula similitud entre dos textos (0-1)
     */
    static similarity(s1, s2) {
        const longer = s1.length > s2.length ? s1 : s2;
        const shorter = s1.length > s2.length ? s2 : s1;

        if (longer.length === 0) return 1.0;

        return (longer.length - this.editDistance(longer, shorter)) / parseFloat(longer.length);
    }

    /**
     * Distancia de edición (Levenshtein)
     */
    static editDistance(s1, s2) {
        s1 = s1.toLowerCase();
        s2 = s2.toLowerCase();

        const costs = [];
        for (let i = 0; i <= s1.length; i++) {
            let lastValue = i;
            for (let j = 0; j <= s2.length; j++) {
                if (i === 0) {
                    costs[j] = j;
                } else {
                    if (j > 0) {
                        let newValue = costs[j - 1];
                        if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
                            newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
                        }
                        costs[j - 1] = lastValue;
                        lastValue = newValue;
                    }
                }
            }
            if (i > 0) costs[s2.length] = lastValue;
        }
        return costs[s2.length];
    }

    /**
     * Detecta si un texto contiene palabra de activación
     */
    static detectWakeWord(transcript, wakeWords, threshold = 0.8) {
        const normalizedTranscript = transcript.toLowerCase().trim();

        return wakeWords.some(wakeWord =>
            normalizedTranscript.includes(wakeWord) ||
            this.similarity(normalizedTranscript, wakeWord) > threshold
        );
    }

    /**
     * Formatea fecha/hora
     */
    static formatDateTime(date = new Date()) {
        return date.toLocaleString('es-ES');
    }

    /**
     * Formatea tiempo
     */
    static formatTime(date = new Date()) {
        return date.toLocaleTimeString('es-ES');
    }

    /**
     * Escapa HTML para prevenir XSS
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Logging estructurado
     */
    static log(level, component, message, data = {}) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            component,
            message,
            ...data
        };

        const emoji = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'debug': '🔍'
        }[level] || '📝';

        console.log(`${emoji} [${component}] ${message}`, data);

        return logEntry;
    }

    /**
     * Manejo de errores estructurado
     */
    static handleError(component, method, error, context = {}) {
        this.log('error', component, `Error in ${method}`, {
            error: error.message,
            stack: error.stack,
            context
        });
    }

    /**
     * Debounce para funciones
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Valida estructura de datos de producto
     */
    static validateProduct(producto) {
        return producto &&
               typeof producto === 'object' &&
               producto.id_articulo &&
               producto.nombre;
    }

    /**
     * Formatea precio
     */
    static formatPrice(price) {
        const parsed = parseFloat(price || 0);
        return `S/ ${parsed.toFixed(2)}`;
    }

    /**
     * Obtiene color de stock
     */
    static getStockColor(stock) {
        const stockNum = parseInt(stock || 0);
        if (stockNum === 0) return 'danger';
        if (stockNum < 10) return 'warning';
        return 'success';
    }

    /**
     * Crea un delay (Promise)
     */
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}