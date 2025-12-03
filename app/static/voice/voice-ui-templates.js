// static/voice/voice-ui-templates.js
// Templates HTML separados para mejor mantenibilidad

import { VoiceUtils } from './voice-utils.js';

export class VoiceUITemplates {
    /**
     * Notificación de activación
     */
    static wakeNotification() {
        return `
            <div class="alert alert-success text-center">
                <i class="bi bi-mic-fill fs-4 me-2"></i>
                <strong>¡Asistente activado!</strong>
                <div class="mt-2">Puedes dar tu comando ahora</div>
                <small class="text-muted d-block mt-2">
                    Ejemplo: "buscar lápices" o "registrar entrada"
                </small>
            </div>
        `;
    }

    /**
     * Card de producto para selección
     */
    static productCard(producto, data) {
        const stockActual = producto.stock_actual || 0;
        const stockClass = stockActual > 0 ? 'bg-success' : 'bg-danger';

        return `
            <div class="col-md-6">
                <div class="card h-100 border-primary">
                    <div class="card-body">
                        <h6 class="card-title text-primary">${VoiceUtils.escapeHtml(producto.nombre)}</h6>
                        <div class="mb-2">
                            <span class="badge bg-secondary">${VoiceUtils.escapeHtml(producto.codigo)}</span>
                            ${producto.categoria_nombre ?
                                `<span class="badge bg-info ms-1">${VoiceUtils.escapeHtml(producto.categoria_nombre)}</span>`
                                : ''}
                        </div>
                        <div class="row small text-muted">
                            <div class="col-6">
                                ${data.intencion === 'REGISTRAR_ENTRADA' ?
                                    `<strong class="text-primary">Costo: ${VoiceUtils.formatPrice(producto.precio_compra)}</strong>` :
                                    `Costo: ${VoiceUtils.formatPrice(producto.precio_compra)}`
                                }
                            </div>
                            <div class="col-6">
                                ${data.intencion === 'REGISTRAR_SALIDA' ?
                                    `<strong class="text-success">Venta: ${VoiceUtils.formatPrice(producto.precio_venta)}</strong>` :
                                    `Venta: ${VoiceUtils.formatPrice(producto.precio_venta)}`
                                }
                            </div>
                        </div>
                        <div class="row small text-muted mt-1">
                            <div class="col-12">
                                Stock: <span class="badge ${stockClass}">${stockActual}</span>
                            </div>
                        </div>
                        <button class="btn btn-primary btn-sm w-100 mt-2"
                                data-action="select-product"
                                data-product-id="${producto.id_articulo}">
                            <i class="bi bi-check-circle me-1"></i> Seleccionar
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Fila de tabla de producto
     */
    static productTableRow(producto, data) {
        const stockActual = producto.stock_actual || 0;
        const stockClass = VoiceUtils.getStockColor(stockActual);
        const stockText = stockActual > 0 ? 'Disponible' : 'Sin stock';
        const estadoClass = (producto.estado === 'ACTIVO' || !producto.estado) ? 'bg-success' : 'bg-secondary';
        const estadoText = producto.estado || 'ACTIVO';

        return `
            <tr>
                <td>
                    <span class="badge bg-primary">${VoiceUtils.escapeHtml(producto.codigo || 'N/A')}</span>
                </td>
                <td>
                    <div class="fw-semibold text-primary">${VoiceUtils.escapeHtml(producto.nombre || 'Sin nombre')}</div>
                    ${producto.descripcion ?
                        `<small class="text-muted">${VoiceUtils.escapeHtml(producto.descripcion)}</small>`
                        : ''}
                </td>
                <td>
                    ${producto.categoria_nombre ?
                        `<span class="badge bg-info">${VoiceUtils.escapeHtml(producto.categoria_nombre)}</span>`
                        : '<span class="text-muted">N/A</span>'}
                </td>
                <td>
                    ${producto.marca_nombre ?
                        `<span class="badge bg-dark">${VoiceUtils.escapeHtml(producto.marca_nombre)}</span>`
                        : '<span class="text-muted">N/A</span>'}
                </td>
                <td class="text-end">
                    <strong ${data.intencion === 'REGISTRAR_ENTRADA' ? 'class="text-primary"' : ''}>
                        ${VoiceUtils.formatPrice(producto.precio_compra)}
                    </strong>
                    ${data.intencion === 'REGISTRAR_ENTRADA' ? '<div class="very-small text-primary">Costo</div>' : ''}
                </td>
                <td class="text-end">
                    <strong class="${data.intencion === 'REGISTRAR_SALIDA' ? 'text-success' : 'text-success'}">
                        ${VoiceUtils.formatPrice(producto.precio_venta)}
                    </strong>
                    ${data.intencion === 'REGISTRAR_SALIDA' ? '<div class="very-small text-success">Venta</div>' : ''}
                </td>
                <td class="text-center">
                    <span class="badge bg-${stockClass}">
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
                    <button class="btn btn-outline-primary btn-sm"
                            data-action="more-info"
                            data-product-name="${VoiceUtils.escapeHtml(producto.nombre)}"
                            title="Más información">
                        <i class="bi bi-info-circle"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    /**
     * Tabla completa de productos
     */
    static productTable(productos, data) {
        const rows = productos.map(p => this.productTableRow(p, data)).join('');
        const titulo = data.es_sugerencia ?
            `Sugerencias para "${VoiceUtils.escapeHtml(data.producto)}"` :
            `${data.cantidad_resultados} producto(s) encontrado(s) para "${VoiceUtils.escapeHtml(data.producto)}"`;

        return `
            <div class="p-3 border-bottom ${data.es_sugerencia ? 'bg-warning' : 'bg-light'}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="fw-semibold">${titulo}</span>
                        ${data.es_sugerencia ?
                            '<span class="badge bg-warning text-dark ms-2"><i class="bi bi-lightbulb"></i> Sugerencias</span>'
                            : ''}
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
                        ${rows}
                    </tbody>
                    <tfoot class="table-secondary">
                        <tr>
                            <td colspan="9" class="small text-muted">
                                <i class="bi bi-info-circle me-1"></i>
                                ${data.es_sugerencia ?
                                    'Mostrando productos similares a tu búsqueda' :
                                    `Mostrando ${productos.length} productos`}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        `;
    }

    /**
     * Mensaje de no resultados
     */
    static noResults(searchTerm) {
        return `
            <div class="text-center py-5">
                <i class="bi bi-search text-muted fs-1 mb-3"></i>
                <h5 class="text-muted">No se encontraron productos</h5>
                <p class="text-muted">No hay resultados para "${VoiceUtils.escapeHtml(searchTerm)}"</p>
                <div class="mt-3">
                    <button class="btn btn-outline-primary" data-action="list-all">
                        <i class="bi bi-list-ul me-1"></i>Ver todos los productos
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Pantalla vacía de resultados
     */
    static emptyResults() {
        return `
            <div class="text-center text-muted py-5">
                <i class="bi bi-robot fs-1 text-light mb-3"></i>
                <p>La respuesta del asistente aparecerá aquí</p>
            </div>
        `;
    }

    /**
     * Confirmación de movimiento
     */
    static movementConfirmation(data, intentColor) {
        const producto = data.producto_seleccionado ||
                        (data.productos_encontrados && data.productos_encontrados[0]);
        const tipo = data.intencion === 'REGISTRAR_ENTRADA' ? 'entrada' : 'salida';

        return `
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
                <div class="alert alert-warning">
                    <h5><i class="bi bi-exclamation-triangle me-2"></i>Confirmar Movimiento</h5>
                    <p class="mb-3">${VoiceUtils.escapeHtml(data.mensaje)}</p>

                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Producto:</strong></div>
                        <div class="col-sm-8">${VoiceUtils.escapeHtml(producto.nombre)} (${VoiceUtils.escapeHtml(producto.codigo)})</div>
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
                    <button class="btn btn-success" data-action="confirm-movement">
                        <i class="bi bi-check-circle me-1"></i> Confirmar
                    </button>
                    <button class="btn btn-secondary" data-action="cancel-movement">
                        <i class="bi bi-x-circle me-1"></i> Cancelar
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Grid de productos para selección
     */
    static productSelectionGrid(productos, data) {
        const cards = productos.map(p => this.productCard(p, data)).join('');

        return `
            <div class="p-3 border-bottom bg-warning">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="fw-semibold">Selecciona un producto</span>
                        <small class="text-dark ms-2">${VoiceUtils.escapeHtml(data.mensaje)}</small>
                    </div>
                </div>
            </div>
            <div class="p-3">
                <div class="row g-3">
                    ${cards}
                </div>
            </div>
        `;
    }
}