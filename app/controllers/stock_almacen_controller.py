from flask import Blueprint, render_template, request, jsonify
from app.models.stock_almacen_model import StockAlmacenModel
from app.models.almacen_model import AlmacenModel
from app.models.articulo_model import ArticuloModel
from app.controllers.auth_controller import login_required, role_required
from app.utils.pagination import Paginator, apply_filters, search_items

stock_almacen_bp = Blueprint('stock_almacen_bp', __name__)
stock_model = StockAlmacenModel()
almacen_model = AlmacenModel()
articulo_model = ArticuloModel()


@stock_almacen_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_stock():
    """Muestra el listado de todo el stock con paginación y filtros."""
    # Obtener todos los datos
    stock = stock_model.get_all_stock()
    almacenes = almacen_model.get_all_almacenes()

    # Obtener parámetros de filtro
    filtro_almacen = request.args.get('almacen', '')
    filtro_estado = request.args.get('estado', '')
    search = request.args.get('search', '')

    # Aplicar filtros si existen
    filters = {}
    if filtro_almacen:
        filters['id_almacen'] = filtro_almacen
    if filtro_estado:
        filters['estado_stock'] = filtro_estado

    stock = apply_filters(stock, filters)

    # Aplicar búsqueda si existe
    if search:
        stock = search_items(stock, search, ['articulo_nombre', 'articulo_codigo', 'almacen_nombre'])

    # Aplicar paginación
    paginator = Paginator(stock, default_per_page=10)

    return render_template(
        'stock_almacen/list.html',
        stock=paginator.get_items(),
        almacenes=almacenes,
        pagination=paginator.get_pagination_data(),
        filtro_almacen=filtro_almacen,
        filtro_estado=filtro_estado,
        search=search
    )


@stock_almacen_bp.route('/bajo')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_stock_bajo():
    """Muestra artículos con stock bajo con paginación."""
    # Obtener stock bajo
    stock_bajo = stock_model.get_stock_bajo()

    # Aplicar búsqueda si existe
    search = request.args.get('search', '')
    if search:
        stock_bajo = search_items(stock_bajo, search, ['articulo_nombre', 'articulo_codigo', 'almacen_nombre'])

    # Aplicar paginación
    paginator = Paginator(stock_bajo, default_per_page=10)

    return render_template(
        'stock_almacen/bajo.html',
        stock_bajo=paginator.get_items(),
        pagination=paginator.get_pagination_data(),
        search=search
    )


@stock_almacen_bp.route('/almacen/<int:id_almacen>')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_stock_almacen(id_almacen):
    """Muestra el stock de un almacén específico con paginación."""
    # Obtener datos del almacén
    stock = stock_model.get_stock_by_almacen(id_almacen)
    almacen = almacen_model.get_almacen_by_id(id_almacen)

    # Obtener filtros
    filtro_estado = request.args.get('estado', '')
    search = request.args.get('search', '')

    # Aplicar filtro de estado si existe
    if filtro_estado:
        filters = {'estado_stock': filtro_estado}
        stock = apply_filters(stock, filters)

    # Aplicar búsqueda si existe
    if search:
        stock = search_items(stock, search, ['articulo_nombre', 'articulo_codigo'])

    # Aplicar paginación
    paginator = Paginator(stock, default_per_page=10)

    return render_template(
        'stock_almacen/por_almacen.html',
        stock=paginator.get_items(),
        almacen=almacen,
        pagination=paginator.get_pagination_data(),
        filtro_estado=filtro_estado,
        search=search
    )


@stock_almacen_bp.route('/actualizar', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def actualizar_stock():
    """Actualiza el stock de un artículo (AJAX)."""
    try:
        id_articulo = int(request.form.get('id_articulo'))
        id_almacen = int(request.form.get('id_almacen'))
        stock_actual = int(request.form.get('stock_actual'))

        if stock_model.update_stock(id_articulo, id_almacen, stock_actual):
            return jsonify({'success': True, 'message': 'Stock actualizado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al actualizar stock'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})