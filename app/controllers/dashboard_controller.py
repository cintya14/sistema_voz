from flask import Blueprint, render_template
from app.models.articulo_model import ArticuloModel
from app.models.almacen_model import AlmacenModel
from app.models.movimiento_model import MovimientoModel
from app.models.stock_almacen_model import StockAlmacenModel
from app.controllers.auth_controller import login_required

dashboard_bp = Blueprint('dashboard_bp', __name__)
articulo_model = ArticuloModel()
almacen_model = AlmacenModel()
movimiento_model = MovimientoModel()
stock_model = StockAlmacenModel()


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Renderiza el dashboard principal."""
    # Obtener datos para las tarjetas
    articulos = articulo_model.get_all_articulos()
    almacenes = almacen_model.get_all_almacenes()

    # Obtener stock bajo y crítico
    stock_bajo = stock_model.get_stock_bajo()
    stock_bajo_count = len(stock_bajo)
    stock_critico_count = len([item for item in stock_bajo if item['faltante'] > 10])  # Ejemplo

    # Obtener movimientos recientes (últimos 5)
    movimientos_recientes = movimiento_model.get_all_movimientos()[:5]

    return render_template('dashboard.html',
                           total_articulos=len(articulos),
                           total_almacenes=len(almacenes),
                           stock_bajo_count=stock_bajo_count,
                           stock_critico_count=stock_critico_count,
                           stock_bajo=stock_bajo,
                           movimientos_recientes=movimientos_recientes)