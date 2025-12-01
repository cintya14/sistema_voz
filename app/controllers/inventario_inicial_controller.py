from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models.inventario_inicial_model import InventarioInicialModel
from app.models.almacen_model import AlmacenModel
from app.models.articulo_model import ArticuloModel
from app.models.stock_almacen_model import StockAlmacenModel
from app.models.movimiento_model import MovimientoModel
from app.controllers.auth_controller import login_required, role_required
from datetime import datetime

inventario_inicial_bp = Blueprint('inventario_inicial_bp', __name__)
inventario_model = InventarioInicialModel()
almacen_model = AlmacenModel()
articulo_model = ArticuloModel()
stock_model = StockAlmacenModel()
movimiento_model = MovimientoModel()


@inventario_inicial_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_inventario_inicial():
    """Muestra el listado de inventario inicial con paginación y búsqueda."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10  # Registros por página

    # Obtener todos los registros de inventario inicial
    all_inventario = inventario_model.get_all_inventario_inicial()

    # Filtrar por búsqueda si existe
    if search:
        filtered_inventario = [
            inv for inv in all_inventario
            if (search.lower() in inv['articulo_nombre'].lower() or
                search.lower() in inv['almacen_nombre'].lower() or
                search.lower() in inv['articulo_codigo'].lower())
        ]
    else:
        filtered_inventario = all_inventario

    # Calcular paginación
    total = len(filtered_inventario)
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    offset = (page - 1) * per_page

    # Obtener solo los registros de la página actual
    inventario_pagina = filtered_inventario[offset:offset + per_page]

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

    inventario = Pagination(inventario_pagina, page, per_page, total)

    return render_template('inventario_inicial/list.html', inventario=inventario, search=search)



@inventario_inicial_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_inventario_inicial():
    almacenes = almacen_model.get_all_almacenes()
    articulos = articulo_model.get_all_articulos()

    if request.method == 'POST':
        fecha = request.form.get('fecha')
        id_almacen = int(request.form.get('id_almacen'))
        id_articulo = int(request.form.get('id_articulo'))
        cantidad = int(request.form.get('cantidad'))
        costo_unitario = float(request.form.get('costo_unitario'))

        # Verificar si ya existe
        if inventario_model.existe_inventario_inicial(id_articulo, id_almacen):
            flash('❌ Ya existe inventario inicial para este artículo', 'error')
            return render_template('inventario_inicial/add.html',
                                   almacenes=almacenes,
                                   articulos=articulos,
                                   fecha_hoy=datetime.now().strftime('%Y-%m-%d'))

        # CREAR inventario inicial
        id_inventario = inventario_model.create_inventario_inicial(fecha, id_almacen, id_articulo, cantidad,
                                                                   costo_unitario)

        if id_inventario:
            # ACTUALIZAR STOCK - ESTA ES LA PARTE CLAVE QUE FALTA
            if stock_model.actualizar_stock_inventario_inicial(id_articulo, id_almacen, cantidad):
                flash('✅ Inventario inicial registrado y stock actualizado', 'success')
                return redirect(url_for('inventario_inicial_bp.list_inventario_inicial'))
            else:
                # Si falla el stock, revertir el inventario
                flash('❌ Error al actualizar stock', 'error')
                # Aquí deberías eliminar el inventario creado o usar transacción
        else:
            flash('❌ Error al registrar inventario inicial', 'error')

    return render_template('inventario_inicial/add.html',
                           almacenes=almacenes,
                           articulos=articulos,
                           fecha_hoy=datetime.now().strftime('%Y-%m-%d'))


@inventario_inicial_bp.route('/ajustar/<int:id_inventario_inicial>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def ajustar_inventario_inicial(id_inventario_inicial):
    """Permite ajustar el inventario inicial mediante un movimiento de ajuste."""
    inventario = inventario_model.get_inventario_inicial_by_id(id_inventario_inicial)

    if not inventario:
        flash('Registro de inventario inicial no encontrado.', 'error')
        return redirect(url_for('inventario_inicial_bp.list_inventario_inicial'))

    if request.method == 'POST':
        nueva_cantidad = int(request.form.get('nueva_cantidad'))
        nuevo_costo = float(request.form.get('nuevo_costo'))
        motivo = request.form.get('motivo')

        # Calcular diferencia
        diferencia = nueva_cantidad - inventario['cantidad']

        if diferencia == 0 and nuevo_costo == inventario['costo_unitario']:
            flash('No hay cambios que aplicar.', 'warning')
            return redirect(url_for('inventario_inicial_bp.list_inventario_inicial'))

        # Crear movimiento de ajuste
        id_usuario = session.get('user_id')

        if diferencia != 0:
            # Determinar tipo de movimiento
            if diferencia > 0:
                id_tipo_movimiento = 3  # AJUSTE POSITIVO
                tipo_movimiento_nombre = "AJUSTE POSITIVO"
            else:
                id_tipo_movimiento = 8  # AJUSTE NEGATIVO
                tipo_movimiento_nombre = "AJUSTE NEGATIVO"

            # Crear movimiento de ajuste
            observacion = f"Ajuste inventario inicial: {motivo}"
            id_movimiento = movimiento_model.create_movimiento(
                datetime.now(),
                inventario['id_almacen'],
                id_tipo_movimiento,
                observacion,
                id_usuario
            )

            if id_movimiento:
                # Agregar detalle del movimiento
                movimiento_model.agregar_detalle_movimiento(
                    id_movimiento,
                    inventario['id_articulo'],
                    abs(diferencia),
                    inventario['costo_unitario']
                )

                # Procesar el movimiento
                if movimiento_model.actualizar_stock(id_movimiento):
                    # Actualizar el registro de inventario inicial
                    inventario_model.update_inventario_inicial(
                        id_inventario_inicial,
                        nueva_cantidad,
                        nuevo_costo
                    )
                    flash(f'Inventario inicial ajustado exitosamente. Se creó movimiento de {tipo_movimiento_nombre}.',
                          'success')
                else:
                    flash('Error al procesar el ajuste de stock.', 'error')
            else:
                flash('Error al crear movimiento de ajuste.', 'error')
        else:
            # Solo cambio de costo
            inventario_model.update_inventario_inicial(
                id_inventario_inicial,
                inventario['cantidad'],
                nuevo_costo
            )
            flash('Costo unitario actualizado exitosamente.', 'success')

        return redirect(url_for('inventario_inicial_bp.list_inventario_inicial'))

    return render_template('inventario_inicial/ajustar.html', inventario=inventario)


@inventario_inicial_bp.route('/verificar_existente/<int:id_articulo>/<int:id_almacen>')
@login_required
@role_required(['ADMINISTRADOR'])
def verificar_inventario_existente(id_articulo, id_almacen):
    """Verifica si ya existe inventario inicial para un artículo en un almacén (AJAX)."""
    existe = inventario_model.existe_inventario_inicial(id_articulo, id_almacen)
    return jsonify({'existe': existe})


@inventario_inicial_bp.route('/delete/<int:id_inventario_inicial>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_inventario_inicial(id_inventario_inicial):
    """NO permite eliminar inventario inicial por seguridad del sistema."""
    flash(
        '❌ NO se puede eliminar inventario inicial por seguridad del sistema. Use "Ajustar" si necesita corregir valores.',
        'error')
    return redirect(url_for('inventario_inicial_bp.list_inventario_inicial'))