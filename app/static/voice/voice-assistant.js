// static/voice/voice-assistant.js
// Asistente de voz refactorizado - Clase principal

import { VOICE_CONFIG } from './voice-config.js';
import { VoiceUtils } from './voice-utils.js';
import { VoiceUITemplates } from './voice-ui-templates.js';
import { VoiceStateManager } from './voice-state-manager.js';

class VoiceAssistant {
    constructor() {
        this.config = VOICE_CONFIG;
        this.stateManager = new VoiceStateManager();
        this.recognition = null;
        this.wakeWordRecognition = null;
        this.currentActionData = null;

        this.init();
    }

    /**
     * Inicialización
     */
    init() {
        this.setupSpeechRecognition();
        this.setupWakeWordRecognition();
        this.bindEvents();
        this.setupStateListener();
        this.updateConnectionStatus();

        VoiceUtils.log('success', 'VoiceAssistant', 'Asistente de voz inicializado');
    }

    /**
     * Configurar listener de cambios de estado
     */
    setupStateListener() {
        this.stateManager.addListener((from, to) => {
            this.onStateChange(from, to);
        });
    }

    /**
     * Callback cuando cambia el estado
     */
    onStateChange(from, to) {
        VoiceUtils.log('info', 'VoiceAssistant', `Transición: ${from} → ${to}`);

        // Actualizar UI según el nuevo estado
        switch (to) {
            case this.config.STATES.IDLE:
                this.updateUIIdle();
                break;
            case this.config.STATES.AWAKE:
                this.updateUIAwake();
                break;
            case this.config.STATES.LISTENING:
                this.updateUIListening();
                break;
            case this.config.STATES.PROCESSING:
                this.updateUIProcessing();
                break;
            case this.config.STATES.ERROR:
                this.updateUIError();
                break;
        }
    }

    /**
     * Configurar reconocimiento de voz principal
     */
    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showStatus('Error: Navegador no compatible',
                          'Tu navegador no soporta reconocimiento de voz', 'error');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        this.recognition.continuous = this.config.CONTINUOUS;
        this.recognition.interimResults = this.config.INTERIM_RESULTS;
        this.recognition.lang = this.config.LANGUAGE;
        this.recognition.maxAlternatives = this.config.MAX_ALTERNATIVES;

        this.recognition.onstart = () => {
            this.stateManager.setState(this.config.STATES.LISTENING);
            this.showStatus('Grabando audio...', 'Habla ahora - el sistema está escuchando', 'info');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.processCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            this.handleRecognitionError(event.error);
        };

        this.recognition.onend = () => {
            if (this.stateManager.isListening()) {
                this.stateManager.setState(this.config.STATES.AWAKE);
            }
        };
    }

    /**
     * Configurar reconocimiento de palabra de activación
     */
    setupWakeWordRecognition() {
        if (!('webkitSpeechRecognition' in window)) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.wakeWordRecognition = new SpeechRecognition();

        this.wakeWordRecognition.continuous = true;
        this.wakeWordRecognition.interimResults = false;
        this.wakeWordRecognition.lang = this.config.LANGUAGE;
        this.wakeWordRecognition.maxAlternatives = 1;

        this.wakeWordRecognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();

            if (VoiceUtils.detectWakeWord(transcript, this.config.WAKE_WORDS, this.config.SIMILARITY_THRESHOLD)) {
                VoiceUtils.log('success', 'WakeWord', `Palabra detectada: ${transcript}`);
                this.wakeUp();
            }
        };

        this.wakeWordRecognition.onerror = (event) => {
            if (event.error !== 'no-speech') {
                VoiceUtils.log('warning', 'WakeWord', `Error: ${event.error}`);
            }
        };

        this.startWakeWordListening();
    }

    /**
     * Iniciar escucha de palabra de activación
     */
    async startWakeWordListening() {
        if (!this.wakeWordRecognition || this.stateManager.isAwake()) return;

        try {
            this.wakeWordRecognition.stop();
            await VoiceUtils.delay(this.config.WAKE_TIMEOUT);

            this.wakeWordRecognition.start();
            this.stateManager.setState(this.config.STATES.LISTENING_WAKE);
            VoiceUtils.log('info', 'WakeWord', 'Escuchando palabra de activación...');
        } catch (error) {
            VoiceUtils.handleError('VoiceAssistant', 'startWakeWordListening', error);
            await VoiceUtils.delay(this.config.RETRY_DELAY);
            this.startWakeWordListening();
        }
    }

    /**
     * Detener escucha de palabra de activación
     */
    stopWakeWordListening() {
        if (this.wakeWordRecognition) {
            try {
                this.wakeWordRecognition.stop();
            } catch (error) {
                VoiceUtils.handleError('VoiceAssistant', 'stopWakeWordListening', error);
            }
        }
    }

    /**
     * Activar el asistente
     */
    wakeUp() {
        if (this.stateManager.isAwake()) return;

        this.stateManager.setState(this.config.STATES.AWAKE);
        this.stopWakeWordListening();

        this.showWakeNotification();

        setTimeout(() => {
            this.startListening();
        }, this.config.WAKE_TIMEOUT);
    }

    /**
     * Dormir el asistente
     */
    async sleep() {
        this.stateManager.setState(this.config.STATES.IDLE);

        await VoiceUtils.delay(this.config.RETRY_DELAY);
        this.startWakeWordListening();

        const msg = this.config.MESSAGES.IDLE;
        this.showStatus(msg.title, msg.detail, 'info');
    }

    /**
     * Iniciar escucha principal
     */
    startListening() {
        if (!this.recognition) {
            this.showStatus('Error de configuración', 'Reconocimiento de voz no disponible', 'error');
            return;
        }

        if (!this.stateManager.isAwake()) {
            this.wakeUp();
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            VoiceUtils.handleError('VoiceAssistant', 'startListening', error);
            this.showStatus('Error al iniciar', 'No se pudo iniciar la grabación', 'error');
        }
    }

    /**
     * Detener escucha
     */
    stopListening() {
        if (this.recognition && this.stateManager.isListening()) {
            this.recognition.stop();
        }

        if (this.stateManager.isAwake()) {
            setTimeout(() => {
                this.sleep();
            }, this.config.RETRY_DELAY);
        }
    }

    /**
     * Toggle listening
     */
    toggleListening() {
        if (!this.stateManager.isAwake()) {
            this.wakeUp();
            return;
        }

        if (this.stateManager.isListening()) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    /**
     * Procesar comando de voz
     */
    processCommand(commandText) {
        const sanitized = VoiceUtils.sanitizeInput(commandText);

        if (!sanitized) {
            this.showStatus('Comando vacío', 'No se detectó comando válido', 'warning');
            return;
        }

        // Si contiene palabra de activación y no está despierto
        if (VoiceUtils.detectWakeWord(sanitized.toLowerCase(), this.config.WAKE_WORDS) &&
            !this.stateManager.isAwake()) {
            this.wakeUp();
            return;
        }

        this.showCommand(sanitized);
        this.stateManager.setState(this.config.STATES.PROCESSING);
        this.showStatus('Enviando comando...', 'Procesando con el servidor', 'warning');

        fetch(this.config.API.PROCESS, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: sanitized })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            this.handleServerResponse(data);
            this.updateLastUpdateTime();
        })
        .catch(error => {
            VoiceUtils.handleError('VoiceAssistant', 'processCommand', error, { command: sanitized });
            this.showStatus('Error de conexión', 'No se pudo contactar al servidor', 'error');
            this.stateManager.setState(this.config.STATES.ERROR);
        });
    }

    /**
     * Manejar respuesta del servidor
     */
    handleServerResponse(data) {
        this.showDebugInfo(data);

        if (data.error) {
            this.showStatus('Error del servidor', data.message, 'error');
            this.updateConnectionStatus('error');
            this.stateManager.setState(this.config.STATES.ERROR);
            return;
        }

        // Ejecutar movimiento automáticamente si está listo
        if (data.listo_para_ejecutar && data.puede_ejecutar) {
            VoiceUtils.log('info', 'VoiceAssistant', 'Ejecutando movimiento automáticamente');
            this.executeMovement(data);
            return;
        }

        // Mostrar confirmación para movimientos
        if (data.intencion && data.intencion.includes('REGISTRAR_') && data.puede_ejecutar) {
            this.showMovementConfirmation(data);
        } else {
            this.showResult(data);
            this.showSearchResults(data);

            if (this.stateManager.isAwake()) {
                setTimeout(() => {
                    this.sleep();
                }, this.config.RESULT_DISPLAY_TIME);
            }
        }

        this.updateConnectionStatus('success');
        this.stateManager.setState(this.config.STATES.AWAKE);

        if (data.necesita_clarificacion) {
            this.showStatus('Información incompleta', 'El comando requiere más detalles', 'warning');
        } else if (!data.intencion || !data.intencion.includes('REGISTRAR_')) {
            this.showStatus('Comando procesado', 'Solicitud completada exitosamente', 'success');
        }
    }

    /**
     * Manejar errores de reconocimiento
     */
    handleRecognitionError(errorType) {
        this.stateManager.setState(this.config.STATES.ERROR);

        let errorMessage = 'Error desconocido';
        let errorDetail = 'Intenta nuevamente';

        switch(errorType) {
            case 'not-allowed':
                errorMessage = 'Permiso denegado';
                errorDetail = 'El acceso al micrófono está bloqueado';
                break;
            case 'no-speech':
                errorMessage = 'No se detectó voz';
                errorDetail = 'Asegúrate de hablar claramente';
                break;
            case 'audio-capture':
                errorMessage = 'Error de audio';
                errorDetail = 'No se pudo acceder al micrófono';
                break;
            case 'network':
                errorMessage = 'Error de red';
                errorDetail = 'Problema de conectividad';
                break;
        }

        this.showStatus(errorMessage, errorDetail, 'error');
    }

    /**
     * Bind de eventos del DOM
     */
    bindEvents() {
        // Botón de voz principal
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleListening());
        }

        // Event delegation para botones dinámicos
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;

            switch(action) {
                case 'select-product':
                    this.handleProductSelectionById(target.dataset.productId);
                    break;
                case 'confirm-movement':
                    if (this.currentActionData) {
                        this.executeMovement(this.currentActionData);
                    }
                    break;
                case 'cancel-movement':
                    this.clearResults();
                    break;
                case 'more-info':
                    this.processCommand(`más información de ${target.dataset.productName}`);
                    break;
                case 'list-all':
                    this.processCommand('listar todos los productos');
                    break;
            }
        });

        // Comandos de ejemplo
        document.querySelectorAll('.example-command').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.target.textContent.trim()
                    .replace(/"/g, '')
                    .replace(/^.*?"(.*)"$/, '$1');
                this.processCommand(command);
            });
        });

        this.updateLastUpdateTime();
    }

    /**
     * Manejar selección de producto por ID
     */
    handleProductSelectionById(productId) {
    if (!this.currentActionData || !this.currentActionData.productos_encontrados) {
        VoiceUtils.log('warning', 'VoiceAssistant', 'No hay datos de acción disponibles');
        return;
    }

    const producto = this.currentActionData.productos_encontrados.find(
        p => String(p.id_articulo) === String(productId)
    );

    if (producto) {
        this.handleProductSelection(producto, this.currentActionData);
    } else {
        VoiceUtils.log('error', 'VoiceAssistant', 'Producto no encontrado', { productId });
    }
}

    /**
     * Manejar selección de producto
     */
    handleProductSelection(producto, actionData) {
        VoiceUtils.log('info', 'VoiceAssistant', 'Producto seleccionado', { producto });

        actionData.producto_seleccionado = producto;
        actionData.productos_encontrados = [producto];
        actionData.necesita_clarificacion = false;
        actionData.campos_faltantes = [];
        actionData.puede_ejecutar = true;
        actionData.listo_para_ejecutar = true;

        const tipo = actionData.intencion === 'REGISTRAR_ENTRADA' ? 'entrada' : 'salida';
        actionData.mensaje = `✅ ¿Registrar ${tipo} de ${actionData.cantidad} unidades de '${producto.nombre}'?`;

        this.showMovementConfirmation(actionData);
    }

    /**
     * Ejecutar movimiento
     */
    executeMovement(actionData) {
        VoiceUtils.log('info', 'VoiceAssistant', 'Ejecutando movimiento', { actionData });

        this.showStatus('Ejecutando movimiento...', 'Registrando en el sistema', 'warning');

        fetch(this.config.API.EXECUTE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action_data: actionData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                this.showStatus('Error', data.message, 'error');
            } else {
                this.showStatus('Éxito', data.message, 'success');

                if (this.stateManager.isAwake()) {
                    setTimeout(() => {
                        this.sleep();
                    }, this.config.RETRY_DELAY);
                }
            }
        })
        .catch(error => {
            VoiceUtils.handleError('VoiceAssistant', 'executeMovement', error);
            this.showStatus('Error de conexión', 'No se pudo ejecutar el movimiento', 'error');
        });
    }

    // ============================================
    // MÉTODOS DE UI
    // ============================================

    updateUIIdle() {
        this.updateUIButton(false);
        const msg = this.config.MESSAGES.IDLE;
        this.showStatus(msg.title, msg.detail, 'info');
    }

    updateUIAwake() {
        this.updateUIButton(true);
        const msg = this.config.MESSAGES.AWAKE;
        this.showStatus(msg.title, msg.detail, 'success');
    }

    updateUIListening() {
        this.updateUIButton(true);
        const msg = this.config.MESSAGES.LISTENING;
        this.showStatus(msg.title, msg.detail, 'info');
    }

    updateUIProcessing() {
        const msg = this.config.MESSAGES.PROCESSING;
        this.showStatus(msg.title, msg.detail, 'warning');
    }

    updateUIError() {
        this.updateUIButton(false);
    }

    updateUIButton(active) {
        const voiceBtn = document.getElementById('voice-btn');
        if (!voiceBtn) return;

        if (active) {
            voiceBtn.classList.add('recording');
            voiceBtn.innerHTML = '<i class="bi bi-mic-fill fs-2"></i>';
        } else {
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="bi bi-mic fs-2"></i>';
        }
    }

    showWakeNotification() {
        const resultElement = document.getElementById('result-text');
        if (resultElement) {
            resultElement.innerHTML = VoiceUITemplates.wakeNotification();
        }
    }

    showCommand(command) {
        const commandElement = document.getElementById('command-text');
        if (commandElement) {
            commandElement.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-chat-left-quote text-primary me-2"></i>
                    <span class="fw-semibold">"${VoiceUtils.escapeHtml(command)}"</span>
                </div>
            `;
        }
    }

    showStatus(title, detail, type = 'info') {
        const statusElement = document.getElementById('system-status');
        const statusText = document.getElementById('status-text');
        const statusDetail = document.getElementById('status-detail');

        if (statusElement && statusText && statusDetail) {
            if (this.stateManager.isAwake()) {
                statusText.textContent = '🎤 ' + title;
            } else {
                statusText.textContent = title;
            }
            statusDetail.textContent = detail;

            let statusClass = `alert alert-${type} mb-0`;
            if (this.stateManager.isAwake()) {
                statusClass += ' alert-awake';
            }
            statusElement.className = statusClass;
        }
    }

    showResult(data) {
        const resultElement = document.getElementById('result-text');
        if (!resultElement) return;

        const intentColor = this.config.INTENT_COLORS[data.intencion] || 'secondary';

        let html = `
            <div class="border-bottom p-3 bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-${intentColor} me-2">
                            ${data.intencion.replace(/_/g, ' ')}
                        </span>
                        <small class="text-muted">Confianza: ${(data.confianza * 100).toFixed(0)}%</small>
                    </div>
                    <small class="text-muted">${VoiceUtils.formatTime()}</small>
                </div>
            </div>
            <div class="p-3">
                <p class="mb-3">${VoiceUtils.escapeHtml(data.mensaje)}</p>
        `;

        if (data.producto) {
            html += `
                <div class="row mb-2">
                    <div class="col-sm-3"><strong>Producto:</strong></div>
                    <div class="col-sm-9">${VoiceUtils.escapeHtml(data.producto)}</div>
                </div>
            `;
        }

        if (data.cantidad) {
            html += `
                <div class="row mb-2">
                    <div class="col-sm-3"><strong>Cantidad:</strong></div>
                    <div class="col-sm-9">${data.cantidad} unidades</div>
                </div>
            `;
        }

        if (data.necesita_clarificacion && data.campos_faltantes.length > 0) {
            html += `
                <div class="alert alert-warning mt-3">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <div>
                            <strong>Información requerida:</strong>
                            <div class="small">Por favor especifica: ${data.campos_faltantes.join(', ')}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        resultElement.innerHTML = html;
    }

    showSearchResults(data) {
        const resultsContainer = document.getElementById('search-results-container');
        const resultsElement = document.getElementById('search-results');
        const suggestionsContainer = document.getElementById('suggestions-container');

        if (resultsContainer) resultsContainer.classList.add('d-none');
        if (suggestionsContainer) suggestionsContainer.classList.add('d-none');

        // Mostrar productos para selección en movimientos
        if (data.necesita_clarificacion &&
            data.campos_faltantes.includes('producto_especifico') &&
            data.productos_encontrados &&
            data.productos_encontrados.length > 0) {

            this.currentActionData = data;

            if (resultsContainer && resultsElement) {
                resultsContainer.classList.remove('d-none');
                resultsElement.innerHTML = VoiceUITemplates.productSelectionGrid(
                    data.productos_encontrados,
                    data
                );
            }
            return;
        }

        // Mostrar resultados de búsqueda
        if (data.productos_encontrados && data.productos_encontrados.length > 0) {
            if (resultsContainer && resultsElement) {
                resultsContainer.classList.remove('d-none');
                resultsElement.innerHTML = VoiceUITemplates.productTable(
                    data.productos_encontrados,
                    data
                );
            }
        } else if (data.producto) {
            // No hay resultados
            if (resultsContainer && resultsElement) {
                resultsContainer.classList.remove('d-none');
                resultsElement.innerHTML = VoiceUITemplates.noResults(data.producto);
            }
        }
    }

    showMovementConfirmation(data) {
        this.currentActionData = data;

        const resultElement = document.getElementById('result-text');
        if (!resultElement) return;

        const intentColor = this.config.INTENT_COLORS[data.intencion] || 'secondary';
        resultElement.innerHTML = VoiceUITemplates.movementConfirmation(data, intentColor);
    }

    clearResults() {
        const resultElement = document.getElementById('result-text');
        const resultsContainer = document.getElementById('search-results-container');
        const suggestionsContainer = document.getElementById('suggestions-container');

        if (resultElement) {
            resultElement.innerHTML = VoiceUITemplates.emptyResults();
        }

        if (resultsContainer) resultsContainer.classList.add('d-none');
        if (suggestionsContainer) suggestionsContainer.classList.add('d-none');

        this.currentActionData = null;

        if (this.stateManager.isAwake()) {
            this.sleep();
        } else {
            const msg = this.config.MESSAGES.IDLE;
            this.showStatus(msg.title, msg.detail, 'info');
        }
    }

    updateConnectionStatus(status = 'success') {
        const connectionElement = document.getElementById('connection-status');
        if (!connectionElement) return;

        if (status === 'success') {
            connectionElement.className = 'badge bg-success';
            connectionElement.innerHTML = '<i class="bi bi-check-circle me-1"></i>Conectado';
        } else {
            connectionElement.className = 'badge bg-danger';
            connectionElement.innerHTML = '<i class="bi bi-x-circle me-1"></i>Error';
        }
    }

    updateLastUpdateTime() {
        const updateElement = document.getElementById('last-update');
        if (updateElement) {
            updateElement.textContent = VoiceUtils.formatDateTime();
        }
    }

    showDebugInfo(data) {
        const debugElement = document.getElementById('debug-info');
        if (debugElement) {
            debugElement.textContent = JSON.stringify(data, null, 2);
        }
    }

    /**
     * Cleanup y destructor
     */
    destroy() {
        this.stopListening();
        this.stopWakeWordListening();

        if (this.recognition) {
            this.recognition.abort();
            this.recognition = null;
        }

        if (this.wakeWordRecognition) {
            this.wakeWordRecognition.abort();
            this.wakeWordRecognition = null;
        }

        VoiceUtils.log('info', 'VoiceAssistant', 'Destruido y limpiado');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.voiceAssistant = new VoiceAssistant();
    VoiceUtils.log('success', 'App', 'Sistema de voz listo');
});