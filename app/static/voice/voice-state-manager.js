// static/voice/voice-state-manager.js
// Gestión de estados del asistente de voz

import { VOICE_CONFIG, STATE_TRANSITIONS } from './voice-config.js';
import { VoiceUtils } from './voice-utils.js';

export class VoiceStateManager {
    constructor() {
        this.currentState = VOICE_CONFIG.STATES.IDLE;
        this.previousState = null;
        this.stateHistory = [];
        this.listeners = [];
    }

    /**
     * Obtiene el estado actual
     */
    getState() {
        return this.currentState;
    }

    /**
     * Verifica si está en un estado específico
     */
    isState(state) {
        return this.currentState === state;
    }

    /**
     * Verifica si la transición es válida
     */
    canTransitionTo(newState) {
        const allowedTransitions = STATE_TRANSITIONS[this.currentState] || [];
        return allowedTransitions.includes(newState);
    }

    /**
     * Cambia el estado
     */
    setState(newState) {
        // Validar que el estado existe
        if (!Object.values(VOICE_CONFIG.STATES).includes(newState)) {
            VoiceUtils.log('error', 'StateManager', `Estado inválido: ${newState}`);
            return false;
        }

        // Validar transición
        if (!this.canTransitionTo(newState)) {
            VoiceUtils.log('warning', 'StateManager',
                `Transición inválida: ${this.currentState} → ${newState}`);
            return false;
        }

        // Guardar estado anterior
        this.previousState = this.currentState;
        this.currentState = newState;

        // Agregar a historial
        this.stateHistory.push({
            from: this.previousState,
            to: newState,
            timestamp: new Date()
        });

        // Mantener solo últimos 10 estados
        if (this.stateHistory.length > 10) {
            this.stateHistory.shift();
        }

        // Log de transición
        VoiceUtils.log('info', 'StateManager',
            `Estado cambiado: ${this.previousState} → ${newState}`);

        // Notificar a listeners
        this.notifyListeners(this.previousState, newState);

        return true;
    }

    /**
     * Registra un listener para cambios de estado
     */
    addListener(callback) {
        if (typeof callback === 'function') {
            this.listeners.push(callback);
        }
    }

    /**
     * Remueve un listener
     */
    removeListener(callback) {
        this.listeners = this.listeners.filter(cb => cb !== callback);
    }

    /**
     * Notifica a todos los listeners
     */
    notifyListeners(from, to) {
        this.listeners.forEach(callback => {
            try {
                callback(from, to);
            } catch (error) {
                VoiceUtils.handleError('StateManager', 'notifyListeners', error);
            }
        });
    }

    /**
     * Obtiene el historial de estados
     */
    getHistory() {
        return [...this.stateHistory];
    }

    /**
     * Resetea el estado a IDLE
     */
    reset() {
        this.previousState = this.currentState;
        this.currentState = VOICE_CONFIG.STATES.IDLE;
        this.stateHistory = [];
        VoiceUtils.log('info', 'StateManager', 'Estado reseteado a IDLE');
    }

    /**
     * Verifica si está despierto (awake o listening)
     */
    isAwake() {
        return this.currentState === VOICE_CONFIG.STATES.AWAKE ||
               this.currentState === VOICE_CONFIG.STATES.LISTENING ||
               this.currentState === VOICE_CONFIG.STATES.PROCESSING;
    }

    /**
     * Verifica si está escuchando
     */
    isListening() {
        return this.currentState === VOICE_CONFIG.STATES.LISTENING ||
               this.currentState === VOICE_CONFIG.STATES.LISTENING_WAKE;
    }

    /**
     * Verifica si está procesando
     */
    isProcessing() {
        return this.currentState === VOICE_CONFIG.STATES.PROCESSING;
    }

    /**
     * Verifica si está en error
     */
    isError() {
        return this.currentState === VOICE_CONFIG.STATES.ERROR;
    }

    /**
     * Obtiene el mensaje del estado actual
     */
    getStateMessage() {
        return VOICE_CONFIG.MESSAGES[this.currentState] || {
            title: 'Estado desconocido',
            detail: ''
        };
    }
}