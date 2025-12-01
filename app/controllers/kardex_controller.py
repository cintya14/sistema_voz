from flask import Blueprint, render_template, request, redirect, url_for
from app.models.kardex_model import KardexModel
from app.models.articulo_model import ArticuloModel
from app.models.almacen_model import AlmacenModel
from app.controllers.auth_controller import login_required, role_required

kardex_bp = Blueprint('kardex_bp', __name__)
kardex_model = KardexModel()
articulo_model = ArticuloModel()
almacen_model = AlmacenModel()

@kardex_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def index_kardex():
    """Página principal del kardex."""
    articulos = articulo_model.get_all_articulos()
    almacenes = almacen_model.get_all_almacenes()
    return render_template('kardex/index.html', articulos=articulos, almacenes=almacenes)

@kardex_bp.route('/articulo', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def kardex_articulo():
    """Muestra el kardex de un artículo."""
    if request.method == 'POST':
        try:
            id_articulo = int(request.form.get('id_articulo'))
            id_almacen = request.form.get('id_almacen')
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')

            # Convertir a None si está vacío
            id_almacen = int(id_almacen) if id_almacen else None

            print(f"DEBUG: Consultando kardex para artículo {id_articulo}, almacén {id_almacen}")

            kardex = kardex_model.get_kardex_articulo(id_articulo, id_almacen, fecha_inicio, fecha_fin)
            articulo = articulo_model.get_articulo_by_id(id_articulo)
            almacenes = almacen_model.get_all_almacenes()

            if not articulo:
                return redirect(url_for('kardex_bp.index_kardex'))

            return render_template('kardex/articulo.html',
                                 kardex=kardex,
                                 articulo=articulo,
                                 almacenes=almacenes,
                                 filtros=request.form)
        except Exception as e:
            print(f"ERROR en kardex_articulo: {e}")
            return redirect(url_for('kardex_bp.index_kardex'))
    else:
        return redirect(url_for('kardex_bp.index_kardex'))

@kardex_bp.route('/almacen', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def kardex_almacen():
    """Muestra el kardex de un almacén."""
    if request.method == 'POST':
        try:
            id_almacen = int(request.form.get('id_almacen'))
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')

            print(f"DEBUG: Consultando kardex para almacén {id_almacen}")

            kardex = kardex_model.get_kardex_almacen(id_almacen, fecha_inicio, fecha_fin)
            almacen = almacen_model.get_almacen_by_id(id_almacen)
            almacenes = almacen_model.get_all_almacenes()

            if not almacen:
                return redirect(url_for('kardex_bp.index_kardex'))

            return render_template('kardex/almacen.html',
                                 kardex=kardex,
                                 almacen=almacen,
                                 almacenes=almacenes,
                                 filtros=request.form)
        except Exception as e:
            print(f"ERROR en kardex_almacen: {e}")
            return redirect(url_for('kardex_bp.index_kardex'))
    else:
        return redirect(url_for('kardex_bp.index_kardex'))