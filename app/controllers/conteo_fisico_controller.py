from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models.conteo_fisico_model import ConteoFisicoModel
from app.models.almacen_model import AlmacenModel
from app.models.articulo_model import ArticuloModel
from app.models.stock_almacen_model import StockAlmacenModel
from app.controllers.auth_controller import login_required, role_required
from datetime import datetime

conteo_fisico_bp = Blueprint('conteo_fisico_bp', __name__)
conteo_model = ConteoFisicoModel()
almacen_model = AlmacenModel()
articulo_model = ArticuloModel()
stock_model = StockAlmacenModel()

@conteo_fisico_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_conteos():
    """Muestra el listado de conteos físicos."""
    conteos = conteo_model.get_all_conteos()
    return render_template('conteo_fisico/list.html', conteos=conteos)

@conteo_fisico_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def add_conteo():
    """Crea un nuevo conteo físico."""
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        id_almacen = int(request.form.get('id_almacen'))
        observaciones = request.form.get('observaciones')
        # El usuario responsable es el que está logueado
        id_usuario = session.get('user_id')

        id_conteo = conteo_model.create_conteo(fecha_inicio, id_almacen, id_usuario, observaciones)
        if id_conteo:
            flash('Conteo físico creado exitosamente. Ahora puede agregar artículos.', 'success')
            return redirect(url_for('conteo_fisico_bp.detalle_conteo', id_conteo=id_conteo))
        else:
            flash('Error al crear conteo físico.', 'error')

    almacenes = almacen_model.get_all_almacenes()
    return render_template('conteo_fisico/add.html', almacenes=almacenes, fecha_hoy=datetime.now().strftime('%Y-%m-%d'))

@conteo_fisico_bp.route('/detalle/<int:id_conteo>')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def detalle_conteo(id_conteo):
    """Muestra el detalle de un conteo físico."""
    conteo = conteo_model.get_conteo_by_id(id_conteo)
    if not conteo:
        flash('Conteo no encontrado.', 'error')
        return redirect(url_for('conteo_fisico_bp.list_conteos'))

    detalle = conteo_model.get_detalle_conteo(id_conteo)
    articulos = articulo_model.get_all_articulos()
    # Obtener stock actual de los artículos en el almacén del conteo
    stock_actual = stock_model.get_stock_by_almacen(conteo['id_almacen'])

    return render_template('conteo_fisico/detalle.html',
                         conteo=conteo,
                         detalle=detalle,
                         articulos=articulos,
                         stock_actual=stock_actual)

@conteo_fisico_bp.route('/agregar_articulo', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def agregar_articulo_conteo():
    """Agrega un artículo al conteo físico."""
    try:
        id_conteo = int(request.form.get('id_conteo'))
        id_articulo = int(request.form.get('id_articulo'))
        stock_contado = int(request.form.get('stock_contado'))

        # Obtener stock del sistema
        conteo = conteo_model.get_conteo_by_id(id_conteo)
        stock_almacen = stock_model.get_stock_by_almacen(conteo['id_almacen'])
        stock_sistema = 0
        for item in stock_almacen:
            if item['id_articulo'] == id_articulo:
                stock_sistema = item['stock_actual']
                break

        if conteo_model.agregar_detalle_conteo(id_conteo, id_articulo, stock_sistema, stock_contado):
            return jsonify({'success': True, 'message': 'Artículo agregado al conteo'})
        else:
            return jsonify({'success': False, 'message': 'Error al agregar artículo'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@conteo_fisico_bp.route('/finalizar/<int:id_conteo>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def finalizar_conteo(id_conteo):
    """Finaliza un conteo físico."""
    if conteo_model.finalizar_conteo(id_conteo, datetime.now()):
        flash('Conteo finalizado exitosamente.', 'success')
    else:
        flash('Error al finalizar conteo.', 'error')
    return redirect(url_for('conteo_fisico_bp.detalle_conteo', id_conteo=id_conteo))

@conteo_fisico_bp.route('/ajustar/<int:id_conteo>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def ajustar_conteo(id_conteo):
    """Ajusta el stock basado en el conteo físico."""
    if conteo_model.ajustar_stock(id_conteo):
        flash('Stock ajustado exitosamente según el conteo físico.', 'success')
    else:
        flash('Error al ajustar stock.', 'error')
    return redirect(url_for('conteo_fisico_bp.detalle_conteo', id_conteo=id_conteo))