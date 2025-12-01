from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.articulo_model import ArticuloModel
from app.models.categoria_model import CategoriaModel
from app.models.marca_model import MarcaModel
from app.models.unidad_medida_model import UnidadMedidaModel
from app.controllers.auth_controller import login_required, role_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

articulos_bp = Blueprint('articulos_bp', __name__)
articulo_model = ArticuloModel()
categoria_model = CategoriaModel()
marca_model = MarcaModel()
unidad_model = UnidadMedidaModel()


@articulos_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_articulos():
    """Muestra el listado de artículos con paginación y búsqueda."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10  # Artículos por página

    # Obtener todos los artículos
    all_articulos = articulo_model.get_all_articulos()

    # Filtrar por búsqueda si existe
    if search:
        filtered_articulos = [
            art for art in all_articulos
            if search.lower() in art['nombre'].lower()
        ]
    else:
        filtered_articulos = all_articulos

    # Calcular paginación
    total = len(filtered_articulos)
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    offset = (page - 1) * per_page

    # Obtener solo los artículos de la página actual
    articulos_pagina = filtered_articulos[offset:offset + per_page]

    # Crear objeto de paginación
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page if total > 0 else 1
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            """Genera números de página para mostrar"""
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                        (num > self.page - left_current - 1 and num < self.page + right_current) or
                        num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    articulos = Pagination(articulos_pagina, page, per_page, total)

    return render_template('articulos/list.html', articulos=articulos, search=search)


@articulos_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_articulo():
    """Permite añadir un nuevo artículo."""
    # Obtener datos para los selects
    categorias = categoria_model.get_all_categorias()
    marcas = marca_model.get_all_marcas()
    unidades = unidad_model.get_all_unidades_medida()

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        precio_compra = float(request.form.get('precio_compra', 0))
        precio_venta = float(request.form.get('precio_venta', 0))
        stock_minimo = int(request.form.get('stock_minimo', 0))
        id_categoria = int(request.form.get('id_categoria'))
        id_marca = int(request.form.get('id_marca')) if request.form.get('id_marca') else None
        id_unidad_medida = int(request.form.get('id_unidad_medida'))

        if articulo_model.create_articulo(codigo, nombre, precio_compra, precio_venta,
                                          stock_minimo, id_categoria, id_marca, id_unidad_medida):
            flash('Artículo agregado exitosamente.', 'success')
            return redirect(url_for('articulos_bp.list_articulos'))
        else:
            flash('Error al agregar artículo. El código del artículo ya existe.', 'error')

    return render_template('articulos/add.html',
                           categorias=categorias,
                           marcas=marcas,
                           unidades=unidades)


@articulos_bp.route('/edit/<int:id_articulo>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_articulo(id_articulo):
    """Permite editar un artículo existente."""
    articulo = articulo_model.get_articulo_by_id(id_articulo)

    if not articulo:
        flash('Artículo no encontrado.', 'error')
        return redirect(url_for('articulos_bp.list_articulos'))

    # Obtener datos para los selects
    categorias = categoria_model.get_all_categorias()
    marcas = marca_model.get_all_marcas()
    unidades = unidad_model.get_all_unidades_medida()

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        precio_compra = float(request.form.get('precio_compra', 0))
        precio_venta = float(request.form.get('precio_venta', 0))
        stock_minimo = int(request.form.get('stock_minimo', 0))
        id_categoria = int(request.form.get('id_categoria'))
        id_marca = int(request.form.get('id_marca')) if request.form.get('id_marca') else None
        id_unidad_medida = int(request.form.get('id_unidad_medida'))

        if articulo_model.update_articulo(id_articulo, codigo, nombre, precio_compra,
                                          precio_venta, stock_minimo, id_categoria,
                                          id_marca, id_unidad_medida):
            flash('Artículo actualizado exitosamente.', 'success')
            return redirect(url_for('articulos_bp.list_articulos'))
        else:
            flash('Error al actualizar artículo. El código del artículo ya existe en otro registro.', 'error')

    return render_template('articulos/edit.html',
                           articulo=articulo,
                           categorias=categorias,
                           marcas=marcas,
                           unidades=unidades)


@articulos_bp.route('/delete/<int:id_articulo>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_articulo(id_articulo):
    """Permite eliminar un artículo."""
    if articulo_model.delete_articulo(id_articulo):
        flash('Artículo eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar artículo. Puede estar siendo usado en algún movimiento.', 'error')

    return redirect(url_for('articulos_bp.list_articulos'))

@articulos_bp.route('/api/articulos')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def get_all_articulos():
    """Endpoint para obtener todos los artículos (para búsqueda en tiempo real)"""
    try:
        # Obtener todos los artículos sin paginación
        all_articulos = articulo_model.get_all_articulos()

        # Convertir a formato JSON
        articulos_list = []
        for art in all_articulos:
            articulos_list.append({
                'id_articulo': art['id_articulo'],
                'codigo': art['codigo'],
                'nombre': art['nombre'],
                'precio_compra': float(art['precio_compra']),
                'precio_venta': float(art['precio_venta']),
                'stock_minimo': art['stock_minimo'],
                'categoria_nombre': art['categoria_nombre'],
                'marca_nombre': art['marca_nombre'],
                'unidad_nombre': art['unidad_nombre'],
                'unidad_abreviatura': art['unidad_abreviatura']
            })

        return jsonify({
            'success': True,
            'articulos': articulos_list,
            'total': len(articulos_list)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500