// static/voice/voice.js
// static/voice/voice.js
class VoiceAssistant {
    constructor() {
        this.isListening = false;
        this.isAwake = false; // ✅ NUEVO: Estado de "despierto"
        this.recognition = null;
        this.wakeWordRecognition = null; // ✅ NUEVO: Reconocimiento de activación
        this.setupSpeechRecognition();
        this.setupWakeWordRecognition(); // ✅ NUEVO: Configurar activación por voz
        this.bindEvents();
        this.updateConnectionStatus();
    }

    // ✅ NUEVO: Configurar reconocimiento de palabra de activación
    setupWakeWordRecognition() {
        if (!('webkitSpeechRecognition' in window)) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.wakeWordRecognition = new SpeechRecognition();

        this.wakeWordRecognition.continuous = true; // ✅ Escucha continua
        this.wakeWordRecognition.interimResults = false;
        this.wakeWordRecognition.lang = 'es-ES';
        this.wakeWordRecognition.maxAlternatives = 1;

        this.wakeWordRecognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();

            // ✅ Detectar palabra de activación
            if (this.detectWakeWord(transcript)) {
                console.log('🎯 Palabra de activación detectada:', transcript);
                this.wakeUp();
            }
        };

        this.wakeWordRecognition.onerror = (event) => {
            // No mostrar errores para no molestar al usuario
            if (event.error !== 'no-speech') {
                console.log('Error en reconocimiento de activación:', event.error);
            }
        };

        // ✅ Iniciar escucha de activación
        this.startWakeWordListening();
    }

    // ✅ NUEVO: Detectar palabra de activación
    detectWakeWord(transcript) {
        const wakeWords = [
            'inventario activar',
            'inventario activa',
            'activar inventario',
            'asistente activar',
            'asistente activa',
            'hola inventario',
            'ok inventario'
        ];

        return wakeWords.some(wakeWord =>
            transcript.includes(wakeWord) ||
            this.similarity(transcript, wakeWord) > 0.8
        );
    }

    // ✅ NUEVO: Calcular similitud entre textos
    similarity(s1, s2) {
        const longer = s1.length > s2.length ? s1 : s2;
        const shorter = s1.length > s2.length ? s2 : s1;

        if (longer.length === 0) return 1.0;

        return (longer.length - this.editDistance(longer, shorter)) / parseFloat(longer.length);
    }

    // ✅ NUEVO: Distancia de edición para similitud
    editDistance(s1, s2) {
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

    // ✅ NUEVO: Activar el asistente
    wakeUp() {
        if (this.isAwake) return;

        this.isAwake = true;
        this.stopWakeWordListening(); // ✅ Pausar escucha de activación

        this.showStatus('Asistente activado', '¡Dime tu comando!', 'success');

        // Efecto visual de activación
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.classList.add('recording');
            voiceBtn.innerHTML = '<i class="bi bi-mic-fill fs-2"></i>';
        }

        // Iniciar grabación principal automáticamente
        setTimeout(() => {
            this.startListening();
        }, 500);

        // ✅ Mostrar notificación temporal
        this.showWakeNotification();
    }

    // ✅ NUEVO: Mostrar notificación de activación
    showWakeNotification() {
        const resultElement = document.getElementById('result-text');
        if (resultElement) {
            resultElement.innerHTML = `
                <div class="alert alert-success text-center">
                    <i class="bi bi-mic-fill fs-4 me-2"></i>
                    <strong>¡Asistente activado!</strong>
                    <div class="mt-2">Puedes dar tu comando ahora</div>
                    <small class="text-muted d-block mt-2">Ejemplo: "buscar lápices" o "registrar entrada"</small>
                </div>
            `;
        }
    }

    // ✅ NUEVO: Iniciar escucha de activación
   // ✅ MEJORADO: Iniciar escucha de activación
    startWakeWordListening() {
        if (this.wakeWordRecognition && !this.isListening && !this.isAwake) {
            try {
                // ✅ Detener primero por si acaso ya estaba corriendo
                this.wakeWordRecognition.stop();

                // ✅ Pequeño delay antes de iniciar
                setTimeout(() => {
                    try {
                        this.wakeWordRecognition.start();
                        console.log('🔮 Escuchando palabra de activación...');
                    } catch (startError) {
                        console.log('Error al iniciar escucha de activación:', startError);
                        // ✅ Reintentar después de 2 segundos
                        setTimeout(() => this.startWakeWordListening(), 2000);
                    }
                }, 500);
            } catch (stopError) {
                console.log('Error al detener escucha de activación:', stopError);
                // ✅ Intentar iniciar de todas formas
                setTimeout(() => {
                    try {
                        this.wakeWordRecognition.start();
                        console.log('🔮 Escuchando palabra de activación...');
                    } catch (startError) {
                        console.log('Error crítico al iniciar escucha:', startError);
                    }
                }, 1000);
            }
        }
    }

    // ✅ NUEVO: Detener escucha de activación
    stopWakeWordListening() {
        if (this.wakeWordRecognition) {
            try {
                this.wakeWordRecognition.stop();
            } catch (error) {
                console.log('Error deteniendo escucha de activación:', error);
            }
        }
    }

    // ✅ NUEVO: Dormir el asistente (volver a estado normal)
    sleep() {
        this.isAwake = false;
        this.isListening = false;
        this.updateUIListening(false);

        // Reanudar escucha de activación
        setTimeout(() => {
            this.startWakeWordListening();
        }, 2000);

        this.showStatus('Sistema en espera', 'Di "inventario activar" para comenzar', 'info');
    }

    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showStatus('Error: Navegador no compatible', 'Tu navegador no soporta reconocimiento de voz', 'error');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'es-ES';
        this.recognition.maxAlternatives = 1;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUIListening(true);
            this.showStatus('Grabando audio...', 'Habla ahora - el sistema está escuchando', 'info');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.showStatus('Procesando comando...', 'Analizando tu solicitud', 'warning');
            this.processCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            this.isListening = false;
            this.updateUIListening(false);

            let errorMessage = 'Error desconocido';
            let errorDetail = 'Intenta nuevamente';

            switch(event.error) {
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
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUIListening(false);
        };
    }

    bindEvents() {
        // Botón de voz principal
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleListening());
        }

        // Comandos de ejemplo
        document.querySelectorAll('.example-command').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.target.textContent.trim().replace(/"/g, '').replace(/^.*?"(.*)"$/, '$1');
                this.processCommand(command);
            });
        });

        // Actualizar hora
        this.updateLastUpdateTime();
    }

        // MODIFICAR método startListening
    startListening() {
        if (!this.recognition) {
            this.showStatus('Error de configuración', 'Reconocimiento de voz no disponible', 'error');
            return;
        }

        // ✅ Si no está "despierto", activar primero
        if (!this.isAwake) {
            this.wakeUp();
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            this.showStatus('Error al iniciar', 'No se pudo iniciar la grabación', 'error');
        }
    }

    // MODIFICAR método stopListening
    // MODIFICAR método stopListening
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }


        if (this.isAwake) {
            setTimeout(() => {
                this.sleep();
            }, 2000); // ⬅️ Esperar 2 segundos antes de dormir (para ver resultados)
        }
    }

    // MODIFICAR método toggleListening
    toggleListening() {
        // ✅ Si se hace clic manualmente, activar inmediatamente
        if (!this.isAwake) {
            this.wakeUp();
            return;
        }

        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    // MODIFICAR método processCommand
    processCommand(commandText) {
        // ✅ Si el comando contiene palabra de activación, activar primero
        if (this.detectWakeWord(commandText.toLowerCase()) && !this.isAwake) {
            this.wakeUp();
            return;
        }

        this.showCommand(commandText);
        this.showStatus('Enviando comando...', 'Procesando con el servidor', 'warning');

        fetch('/voice/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: commandText })
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
            this.showStatus('Error de conexión', 'No se pudo contactar al servidor', 'error');
            console.error('Error:', error);
        });
    }

    // MODIFICAR método showStatus para mostrar estado de activación
    showStatus(title, detail, type = 'info') {
        const statusElement = document.getElementById('system-status');
        const statusText = document.getElementById('status-text');
        const statusDetail = document.getElementById('status-detail');

        if (statusElement && statusText && statusDetail) {
            // ✅ Mostrar estado de activación
            if (this.isAwake) {
                statusText.textContent = '🎤 ' + title;
            } else {
                statusText.textContent = title;
            }
            statusDetail.textContent = detail;

            // Clases CSS según tipo y estado
            let statusClass = `alert alert-${type} mb-0`;
            if (this.isAwake) {
                statusClass += ' alert-awake';
            }
            statusElement.className = statusClass;
        }
    }

    handleServerResponse(data) {
    this.showDebugInfo(data);

    if (data.error) {
        this.showStatus('Error del servidor', data.message, 'error');
        this.updateConnectionStatus('error');
        return;
    }

    // ✅ MEJORADO: Ejecutar automáticamente cuando está listo
    if (data.listo_para_ejecutar && data.puede_ejecutar) {
        console.log('🚀 [DEBUG] Ejecutando movimiento automáticamente');
        this.executeMovement(data);
        return;
    }

    // Mostrar confirmación para movimientos que necesitan interacción
    if (data.intencion && data.intencion.includes('REGISTRAR_') && data.puede_ejecutar) {
        this.showMovementConfirmation(data);
    } else {
        this.showResult(data);
        this.showSearchResults(data);

        // ✅ NUEVO: Dormir después de mostrar resultados (solo si fue activado por voz)
        if (this.isAwake) {
            setTimeout(() => {
                this.sleep();
            }, 3000); // ⬅️ Dormir después de 3 segundos de mostrar resultados
        }
    }

    this.updateConnectionStatus('success');

    if (data.necesita_clarificacion) {
        this.showStatus('Información incompleta', 'El comando requiere más detalles', 'warning');
    } else if (!data.intencion || !data.intencion.includes('REGISTRAR_')) {
        this.showStatus('Comando procesado', 'Solicitud completada exitosamente', 'success');
    }
}

    updateUIListening(listening) {
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            if (listening) {
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = '<i class="bi bi-mic-fill fs-2"></i>';
            } else {
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="bi bi-mic fs-2"></i>';
            }
        }
    }

    showCommand(command) {
        const commandElement = document.getElementById('command-text');
        if (commandElement) {
            commandElement.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-chat-left-quote text-primary me-2"></i>
                    <span class="fw-semibold">"${command}"</span>
                </div>
            `;
        }
    }

    showResult(data) {
        const resultContainer = document.getElementById('result-container');
        const resultElement = document.getElementById('result-text');

        if (resultContainer && resultElement) {
            let html = `
                <div class="border-bottom p-3 bg-light">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge bg-${this.getIntentColor(data.intencion)} me-2">
                                ${data.intencion.replace(/_/g, ' ')}
                            </span>
                            <small class="text-muted">Confianza: ${(data.confianza * 100).toFixed(0)}%</small>
                        </div>
                        <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    </div>
                </div>
                <div class="p-3">
                    <p class="mb-3">${data.mensaje}</p>
            `;

            if (data.producto) {
                html += `
                    <div class="row mb-2">
                        <div class="col-sm-3"><strong>Producto:</strong></div>
                        <div class="col-sm-9">${data.producto}</div>
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
    }

    handleProductSelection(producto, actionData) {
        console.log('🎯 [DEBUG] Producto seleccionado:', producto);

        // Actualizar los datos de la acción con el producto seleccionado
        actionData.producto_seleccionado = producto;
        actionData.productos_encontrados = [producto]; // Solo el seleccionado
        actionData.necesita_clarificacion = false;
        actionData.campos_faltantes = [];
        actionData.puede_ejecutar = true;
        actionData.listo_para_ejecutar = true;

        // Generar mensaje de confirmación
        const tipo = actionData.intencion === 'REGISTRAR_ENTRADA' ? 'entrada' : 'salida';
        actionData.mensaje = `✅ ¿Registrar ${tipo} de ${actionData.cantidad} unidades de '${producto.nombre}'?`;

        // Mostrar confirmación inmediata
        this.showMovementConfirmation(actionData);
    }

    showSearchResults(data) {
    console.log('🔍 [DEBUG] showSearchResults llamado con:', data);

    const resultsContainer = document.getElementById('search-results-container');
    const resultsElement = document.getElementById('search-results');
    const suggestionsContainer = document.getElementById('suggestions-container');
    const suggestionsElement = document.getElementById('suggestions-list');

    // Ocultar contenedores primero
    if (resultsContainer) resultsContainer.classList.add('d-none');
    if (suggestionsContainer) suggestionsContainer.classList.add('d-none');

     // ✅ NUEVO: Si es un movimiento que necesita clarificación, mostrar productos para selección
    if (data.necesita_clarificacion && data.campos_faltantes.includes('producto_especifico') &&
        data.productos_encontrados && data.productos_encontrados.length > 0) {

        console.log('🔍 [DEBUG] Mostrando productos para selección de movimiento');

        if (resultsContainer && resultsElement) {
            resultsContainer.classList.remove('d-none');

            let html = `
                <div class="p-3 border-bottom bg-warning">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="fw-semibold">Selecciona un producto</span>
                            <small class="text-dark ms-2">${data.mensaje}</small>
                        </div>
                    </div>
                </div>
                <div class="p-3">
                    <div class="row g-3">
            `;

            data.productos_encontrados.forEach((producto, index) => {
                const stockActual = producto.stock_actual !== undefined ? producto.stock_actual : 0;
                const stockClass = stockActual > 0 ? 'bg-success' : 'bg-danger';

                html += `
               <div class="col-md-6">
                    <div class="card h-100 border-primary">
                        <div class="card-body">
                            <h6 class="card-title text-primary">${producto.nombre}</h6>
                            <div class="mb-2">
                                <span class="badge bg-secondary">${producto.codigo}</span>
                                ${producto.categoria_nombre ? `<span class="badge bg-info ms-1">${producto.categoria_nombre}</span>` : ''}
                            </div>
                            <div class="row small text-muted">
                                <div class="col-6">
                                    ${data.intencion === 'REGISTRAR_ENTRADA' ? 
                                        `<strong class="text-primary">Costo: S/ ${parseFloat(producto.precio_compra || 0).toFixed(2)}</strong>` :
                                        `Costo: S/ ${parseFloat(producto.precio_compra || 0).toFixed(2)}`
                                    }
                                </div>
                                <div class="col-6">
                                    ${data.intencion === 'REGISTRAR_SALIDA' ? 
                                        `<strong class="text-success">Venta: S/ ${parseFloat(producto.precio_venta || 0).toFixed(2)}</strong>` :
                                        `Venta: S/ ${parseFloat(producto.precio_venta || 0).toFixed(2)}`
                                    }
                                </div>
                            </div>
                            <div class="row small text-muted mt-1">
                                <div class="col-12">
                                    Stock: <span class="badge ${stockClass}">${stockActual}</span>
                                </div>
                            </div>
                            <button class="btn btn-primary btn-sm w-100 mt-2" 
                                    onclick="window.voiceAssistant.handleProductSelection(${JSON.stringify(producto).replace(/"/g, '&quot;')}, ${JSON.stringify(data).replace(/"/g, '&quot;')})">
                                <i class="bi bi-check-circle me-1"></i> Seleccionar
                            </button>
                        </div>
                    </div>
               </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;

            resultsElement.innerHTML = html;
        }
        return;
    }

    console.log('🔍 [DEBUG] Productos encontrados:', data.productos_encontrados);
    console.log('🔍 [DEBUG] Es sugerencia?:', data.es_sugerencia);

    // ✅ NUEVO: Mostrar resultados si hay productos encontrados O si son sugerencias
    const mostrarResultados = data.productos_encontrados && data.productos_encontrados.length > 0;

    if (mostrarResultados) {
        console.log('🔍 [DEBUG] Mostrando tabla con productos/sugerencias');

        if (resultsContainer && resultsElement) {
            resultsContainer.classList.remove('d-none');

            // VERIFICAR CAMPOS DEL PRIMER PRODUCTO
            if (data.productos_encontrados.length > 0) {
                const primerProducto = data.productos_encontrados[0];
                console.log('🔍 [DEBUG] Campos del primer producto:', Object.keys(primerProducto));
                console.log('🔍 [DEBUG] Valores del primer producto:', primerProducto);
            }

            // ✅ NUEVO: Título diferente para sugerencias
            const titulo = data.es_sugerencia ?
                `Sugerencias para "${data.producto}"` :
                `${data.cantidad_resultados} producto(s) encontrado(s) para "${data.producto}"`;

            let html = `
                <div class="p-3 border-bottom ${data.es_sugerencia ? 'bg-warning' : 'bg-light'}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="fw-semibold">${titulo}</span>
                            ${data.es_sugerencia ? '<span class="badge bg-warning text-dark ms-2"><i class="bi bi-lightbulb"></i> Sugerencias</span>' : ''}
                        </div>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover table-striped mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th width="80">Código</th>
                                <th>Nombre del Producto</th>
                                <th width="120">Categoría</th>
                                <th width="100">Marca</th>
                                <th width="100">P. Compra</th>
                                <th width="100">P. Venta</th>
                                <th width="100">Stock</th>
                                <th width="100">Estado</th>
                                <th width="80" class="text-center">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            data.productos_encontrados.forEach((producto, index) => {
                console.log(`🔍 [DEBUG] Procesando producto ${index}:`, producto);

                const stockActual = producto.stock_actual !== undefined ? producto.stock_actual : 0;
                const stockClass = stockActual > 0 ? 'bg-success' : 'bg-danger';
                const stockText = stockActual > 0 ? 'Disponible' : 'Sin stock';
                const estadoClass = (producto.estado === 'ACTIVO' || !producto.estado) ? 'bg-success' : 'bg-secondary';
                const estadoText = producto.estado || 'ACTIVO';

                html += `
                    <tr>
                        <td>
                            <span class="badge bg-primary">${producto.codigo || 'N/A'}</span>
                        </td>
                        <td>
                            <div class="fw-semibold text-primary">${producto.nombre || 'Sin nombre'}</div>
                            ${producto.descripcion ? `<small class="text-muted">${producto.descripcion}</small>` : ''}
                        </td>
                        <td>
                            ${producto.categoria_nombre ? `<span class="badge bg-info">${producto.categoria_nombre}</span>` : '<span class="text-muted">N/A</span>'}
                        </td>
                        <td>
                            ${producto.marca_nombre ? `<span class="badge bg-dark">${producto.marca_nombre}</span>` : '<span class="text-muted">N/A</span>'}
                        </td>
                        
                        <td class="text-end">
                            <strong ${data.intencion === 'REGISTRAR_ENTRADA' ? 'class="text-primary"' : ''}>
                                S/ ${parseFloat(producto.precio_compra || 0).toFixed(2)}
                            </strong>
                            ${data.intencion === 'REGISTRAR_ENTRADA' ? '<div class="very-small text-primary">Costo</div>' : ''}
                        </td>
                        <td class="text-end">
                            <strong class="${data.intencion === 'REGISTRAR_SALIDA' ? 'text-success' : 'text-success'}">
                                S/ ${parseFloat(producto.precio_venta || 0).toFixed(2)}
                            </strong>
                            ${data.intencion === 'REGISTRAR_SALIDA' ? '<div class="very-small text-success">Venta</div>' : ''}
                        </td>
                        <td class="text-center">
                            <span class="badge ${stockClass}">
                                <i class="bi bi-box-seam me-1"></i>
                                ${stockActual}
                            </span>
                            <div class="very-small text-muted">${stockText}</div>
                        </td>
                        <td class="text-center">
                            <span class="badge ${estadoClass}">
                                ${estadoText}
                            </span>
                        </td>
                        <td class="text-center">
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" 
                                        onclick="window.voiceAssistant.processCommand('más información de ${producto.nombre}')"
                                        title="Más información">
                                    <i class="bi bi-info-circle"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                        <tfoot class="table-secondary">
                            <tr>
                                <td colspan="9" class="small text-muted">
                                    <i class="bi bi-info-circle me-1"></i>
                                    ${data.es_sugerencia ? 
                                        'Mostrando productos similares a tu búsqueda' : 
                                        `Mostrando ${data.productos_encontrados.length} productos`}
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;

            resultsElement.innerHTML = html;
            console.log('🔍 [DEBUG] Tabla HTML generada');
        }
    } else {
        console.log('🔍 [DEBUG] No hay productos encontrados');
        // Mostrar mensaje de no resultados
        if (resultsContainer && resultsElement) {
            resultsContainer.classList.remove('d-none');
            resultsElement.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-search text-muted fs-1 mb-3"></i>
                    <h5 class="text-muted">No se encontraron productos</h5>
                    <p class="text-muted">No hay resultados para "${data.producto}"</p>
                    <div class="mt-3">
                        <button class="btn btn-outline-primary" onclick="window.voiceAssistant.processCommand('listar todos los productos')">
                            <i class="bi bi-list-ul me-1"></i>Ver todos los productos
                        </button>
                    </div>
                </div>
            `;
        }
    }

    // ✅ NUEVO: Ocultar el contenedor de sugerencias separado ya que ahora se muestran en la tabla principal
    if (suggestionsContainer) {
        suggestionsContainer.classList.add('d-none');
    }
}

    getIntentColor(intent) {
        const colors = {
            'BUSCAR_PRODUCTO': 'info',
            'REGISTRAR_ENTRADA': 'success',
            'REGISTRAR_SALIDA': 'warning',
            'DESCONOCIDO': 'secondary',
            'ERROR': 'danger'
        };
        return colors[intent] || 'secondary';
    }

    updateConnectionStatus(status = 'success') {
        const connectionElement = document.getElementById('connection-status');
        if (connectionElement) {
            if (status === 'success') {
                connectionElement.className = 'badge bg-success';
                connectionElement.innerHTML = '<i class="bi bi-check-circle me-1"></i>Conectado';
            } else {
                connectionElement.className = 'badge bg-danger';
                connectionElement.innerHTML = '<i class="bi bi-x-circle me-1"></i>Error';
            }
        }
    }

    updateLastUpdateTime() {
        const updateElement = document.getElementById('last-update');
        if (updateElement) {
            updateElement.textContent = new Date().toLocaleString('es-ES');
        }
    }

    showDebugInfo(data) {
        const debugElement = document.getElementById('debug-info');
        if (debugElement) {
            debugElement.textContent = JSON.stringify(data, null, 2);
        }
    }

    showMovementConfirmation(data) {
    console.log('🔄 [DEBUG] Mostrando confirmación de movimiento:', data);

    const resultContainer = document.getElementById('result-container');
    const resultElement = document.getElementById('result-text');

    if (resultContainer && resultElement) {
        const producto = data.producto_seleccionado || (data.productos_encontrados && data.productos_encontrados[0]);
        const tipo = data.intencion === 'REGISTRAR_ENTRADA' ? 'entrada' : 'salida';

        let html = `
            <div class="border-bottom p-3 bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-${this.getIntentColor(data.intencion)} me-2">
                            ${data.intencion.replace(/_/g, ' ')}
                        </span>
                        <small class="text-muted">Confianza: ${(data.confianza * 100).toFixed(0)}%</small>
                    </div>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
            <div class="p-3">
                <div class="alert alert-warning">
                    <h5><i class="bi bi-exclamation-triangle me-2"></i>Confirmar Movimiento</h5>
                    <p class="mb-3">${data.mensaje}</p>
                    
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Producto:</strong></div>
                        <div class="col-sm-8">${producto.nombre} (${producto.codigo})</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Cantidad:</strong></div>
                        <div class="col-sm-8">${data.cantidad} unidades</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Tipo:</strong></div>
                        <div class="col-sm-8">${tipo}</div>
                    </div>
                </div>
                
                <div class="d-flex gap-2">
                    <button class="btn btn-success" onclick="window.voiceAssistant.executeMovement(${JSON.stringify(data).replace(/"/g, '&quot;')})">
                        <i class="bi bi-check-circle me-1"></i> Confirmar
                    </button>
                    <button class="btn btn-secondary" onclick="window.voiceAssistant.clearResults()">
                        <i class="bi bi-x-circle me-1"></i> Cancelar
                    </button>
                </div>
            </div>
        `;

        resultElement.innerHTML = html;
    }
}

    executeMovement(actionData) {
    console.log('🚀 [DEBUG] Ejecutando movimiento:', actionData);

    this.showStatus('Ejecutando movimiento...', 'Registrando en el sistema', 'warning');

    fetch('/voice/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action_data: actionData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            this.showStatus('Error', data.message, 'error');
        } else {
            this.showStatus('Éxito', data.message, 'success');

            if (this.isAwake) {
                setTimeout(() => {
                    this.sleep();
                }, 2000);
            }
        }
    })
    .catch(error => {
        this.showStatus('Error de conexión', 'No se pudo ejecutar el movimiento', 'error');
        console.error('Error:', error);
    });
}

    clearResults() {
    const resultElement = document.getElementById('result-text');
    const resultsContainer = document.getElementById('search-results-container');
    const suggestionsContainer = document.getElementById('suggestions-container');

    if (resultElement) {
        resultElement.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-robot fs-1 text-light mb-3"></i>
                <p>La respuesta del asistente aparecerá aquí</p>
            </div>
        `;
    }

    if (resultsContainer) resultsContainer.classList.add('d-none');
    if (suggestionsContainer) suggestionsContainer.classList.add('d-none');

    //
    if (this.isAwake) {
        this.sleep();
    } else {
        this.showStatus('Sistema en espera', 'Di "inventario activar" para comenzar', 'info');
    }
}



}



// Inicializar cuando el DOM esté listo


document.addEventListener('DOMContentLoaded', function() {
    window.voiceAssistant = new VoiceAssistant();
    console.log('✅ Asistente de voz profesional inicializado');
});