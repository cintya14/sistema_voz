from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models.venta_model import VentaModel
from app.models.cliente_model import ClienteModel
from app.models.tipo_documento_model import TipoDocumentoModel
from app.models.serie_documento_model import SerieDocumentoModel
from app.models.articulo_model import ArticuloModel
from app.models.almacen_model import AlmacenModel
from app.models.stock_almacen_model import StockAlmacenModel
from app.controllers.auth_controller import login_required, role_required
from datetime import datetime

ventas_bp = Blueprint('ventas_bp', __name__)
venta_model = VentaModel()
cliente_model = ClienteModel()
tipo_documento_model = TipoDocumentoModel()
serie_documento_model = SerieDocumentoModel()
articulo_model = ArticuloModel()
almacen_model = AlmacenModel()
stock_model = StockAlmacenModel()


@ventas_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def list_ventas():
    """Muestra el listado de ventas."""
    ventas = venta_model.get_all_ventas()
    return render_template('ventas/list.html', ventas=ventas)


@ventas_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def add_venta():
    """Crea una nueva venta."""
    if request.method == 'POST':
        fecha_emision = request.form.get('fecha_emision')
        id_tipo_documento = int(request.form.get('id_tipo_documento'))
        id_serie = int(request.form.get('id_serie'))
        id_cliente = request.form.get('id_cliente')
        id_cliente = int(id_cliente) if id_cliente else None
        id_almacen = int(request.form.get('id_almacen'))
        id_usuario = session.get('user_id')

        # Obtener el número de documento (correlativo)
        serie = serie_documento_model.get_serie_by_id(id_serie)
        if not serie:
            flash('Serie no encontrada.', 'error')
            return redirect(url_for('ventas_bp.add_venta'))

        numero_documento = serie['correlativo_actual'] + 1

        # Por ahora, los totales se calcularán en el detalle, así que los ponemos en 0
        total_gravado = 0
        total_igv = 0
        total_venta = 0

        # Crear la venta
        id_venta = venta_model.create_venta(
            fecha_emision, id_tipo_documento, id_serie, numero_documento, id_cliente, id_usuario, total_gravado,
            total_igv, total_venta
        )

        if id_venta:
            # Incrementar el correlativo de la serie
            serie_documento_model.incrementar_correlativo(id_serie)
            flash('Venta creada exitosamente. Ahora puede agregar artículos.', 'success')
            return redirect(url_for('ventas_bp.detalle_venta', id_venta=id_venta))
        else:
            flash('Error al crear venta.', 'error')

    tipos_documento = tipo_documento_model.get_all_tipos_documento()
    clientes = cliente_model.get_all_clientes()
    almacenes = almacen_model.get_all_almacenes()

    return render_template('ventas/add.html',
                           tipos_documento=tipos_documento,
                           clientes=clientes,
                           almacenes=almacenes,
                           fecha_hoy=datetime.now().strftime('%Y-%m-%dT%H:%M'))


@ventas_bp.route('/detalle/<int:id_venta>')
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def detalle_venta(id_venta):
    """Muestra el detalle de una venta."""
    venta = venta_model.get_venta_by_id(id_venta)
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('ventas_bp.list_ventas'))

    detalle = venta_model.get_detalle_venta(id_venta)
    articulos = articulo_model.get_all_articulos()

    # Calcular totales
    total_gravado = sum(item['subtotal'] / (1 + item['porcentaje_igv'] / 100) for item in detalle)
    total_igv = sum(item['subtotal'] - (item['subtotal'] / (1 + item['porcentaje_igv'] / 100)) for item in detalle)
    total_venta = sum(item['subtotal'] for item in detalle)

    return render_template('ventas/detalle.html',
                           venta=venta,
                           detalle=detalle,
                           articulos=articulos,
                           total_gravado=total_gravado,
                           total_igv=total_igv,
                           total_venta=total_venta)


@ventas_bp.route('/agregar_articulo', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def agregar_articulo_venta():
    """Agrega un artículo a la venta."""
    try:
        id_venta = int(request.form.get('id_venta'))
        id_articulo = int(request.form.get('id_articulo'))
        cantidad = int(request.form.get('cantidad'))
        precio_unitario = float(request.form.get('precio_unitario'))
        porcentaje_igv = 18  # IGV por defecto 18%
        subtotal = cantidad * precio_unitario * (1 + porcentaje_igv / 100)

        if venta_model.agregar_detalle_venta(id_venta, id_articulo, cantidad, precio_unitario, porcentaje_igv,
                                             subtotal):
            return jsonify({'success': True, 'message': 'Artículo agregado a la venta'})
        else:
            return jsonify({'success': False, 'message': 'Error al agregar artículo'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@ventas_bp.route('/procesar/<int:id_venta>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def procesar_venta(id_venta):
    """Procesa una venta y actualiza el stock."""
    # Verificar que la venta tenga artículos
    detalle = venta_model.get_detalle_venta(id_venta)
    if not detalle:
        flash('No se puede procesar una venta sin artículos.', 'error')
        return redirect(url_for('ventas_bp.detalle_venta', id_venta=id_venta))

    # Obtener el almacén de la venta (necesitaríamos guardarlo en la venta)
    # Por ahora, usaremos el almacén principal
    almacen_principal = almacen_model.get_almacen_principal()
    if not almacen_principal:
        flash('No hay almacén principal configurado.', 'error')
        return redirect(url_for('ventas_bp.detalle_venta', id_venta=id_venta))

    if venta_model.actualizar_stock_venta(id_venta, almacen_principal['id_almacen']):
        flash('Venta procesada exitosamente. Stock actualizado.', 'success')
    else:
        flash('Error al procesar venta. Verifique el stock disponible.', 'error')

    return redirect(url_for('ventas_bp.detalle_venta', id_venta=id_venta))


@ventas_bp.route('/anular/<int:id_venta>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def anular_venta(id_venta):
    """Anula una venta."""
    # Obtener el almacén principal
    almacen_principal = almacen_model.get_almacen_principal()
    if not almacen_principal:
        flash('No hay almacén principal configurado.', 'error')
        return redirect(url_for('ventas_bp.list_ventas'))

    if venta_model.anular_venta(id_venta, almacen_principal['id_almacen']):
        flash('Venta anulada exitosamente.', 'success')
    else:
        flash('Error al anular venta.', 'error')

    return redirect(url_for('ventas_bp.list_ventas'))


@ventas_bp.route('/get_series/<int:id_tipo_documento>')
@login_required
def get_series(id_tipo_documento):
    """Obtiene las series por tipo de documento (AJAX)."""
    series = serie_documento_model.get_series_por_tipo(id_tipo_documento)
    return jsonify(series)