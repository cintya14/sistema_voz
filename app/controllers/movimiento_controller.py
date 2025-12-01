from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models.movimiento_model import MovimientoModel
from app.models.tipo_movimiento_model import TipoMovimientoModel
from app.models.almacen_model import AlmacenModel
from app.models.articulo_model import ArticuloModel
from app.models.proveedor_model import ProveedorModel
from app.controllers.auth_controller import login_required, role_required
from app.utils.pagination import Paginator, search_items
from datetime import datetime

movimientos_bp = Blueprint('movimientos_bp', __name__)
movimiento_model = MovimientoModel()
tipo_movimiento_model = TipoMovimientoModel()
almacen_model = AlmacenModel()
articulo_model = ArticuloModel()
proveedor_model = ProveedorModel()


@movimientos_bp.route('/entradas')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_entradas():
    """Muestra el listado de movimientos de entrada con paginación."""
    # Obtener todos los movimientos de entrada
    movimientos = movimiento_model.get_all_movimientos(tipo='entrada')

    # Obtener parámetros de búsqueda (NUEVOS)
    search = request.args.get('search', '')
    id_articulo = request.args.get('id_articulo', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    # Aplicar búsqueda por texto si existe
    if search:
        movimientos = search_items(movimientos, search, [
            'almacen_nombre',
            'tipo_movimiento_nombre',
            'proveedor_nombre',
            'nombre_usuario',
            'observacion'
        ])

    # Aplicar filtro por artículo (NUEVO)
    if id_articulo:
        try:
            id_articulo_int = int(id_articulo)
            # Filtrar movimientos que contengan el artículo
            movimientos_filtrados = []
            for movimiento in movimientos:
                detalle = movimiento_model.get_detalle_movimiento(movimiento['id_movimiento_cabecera'])
                if any(item['id_articulo'] == id_articulo_int for item in detalle):
                    movimientos_filtrados.append(movimiento)
            movimientos = movimientos_filtrados
        except ValueError:
            pass  # Si id_articulo no es un número válido, ignorar

    # Aplicar filtros por fecha (NUEVO)
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            movimientos = [m for m in movimientos if m['fecha_movimiento'] >= fecha_desde_dt]
        except ValueError:
            pass

    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Añadir un día para incluir la fecha hasta
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            movimientos = [m for m in movimientos if m['fecha_movimiento'] <= fecha_hasta_dt]
        except ValueError:
            pass

    # Obtener artículos para el dropdown (NUEVO)
    articulos = articulo_model.get_all_articulos()

    # Aplicar paginación
    paginator = Paginator(movimientos, default_per_page=10)

    return render_template(
        'movimientos/entradas/list.html',
        movimientos=paginator.get_items(),
        pagination=paginator.get_pagination_data(),
        search=search,
        articulos=articulos,  # NUEVO: pasar artículos al template
        id_articulo=id_articulo,  # NUEVO: mantener el artículo seleccionado
        fecha_desde=fecha_desde,  # NUEVO: mantener fecha desde
        fecha_hasta=fecha_hasta   # NUEVO: mantener fecha hasta
    )


@movimientos_bp.route('/salidas')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_salidas():
    """Muestra el listado de movimientos de salida con paginación."""
    # Obtener todos los movimientos de salida
    movimientos = movimiento_model.get_all_movimientos(tipo='salida')

    # Obtener parámetros de búsqueda (NUEVOS)
    search = request.args.get('search', '')
    id_articulo = request.args.get('id_articulo', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    # Aplicar búsqueda por texto si existe
    if search:
        movimientos = search_items(movimientos, search, [
            'almacen_nombre',
            'tipo_movimiento_nombre',
            'nombre_usuario',
            'observacion'
        ])

    # Aplicar filtro por artículo (NUEVO)
    if id_articulo:
        try:
            id_articulo_int = int(id_articulo)
            # Filtrar movimientos que contengan el artículo
            movimientos_filtrados = []
            for movimiento in movimientos:
                detalle = movimiento_model.get_detalle_movimiento(movimiento['id_movimiento_cabecera'])
                if any(item['id_articulo'] == id_articulo_int for item in detalle):
                    movimientos_filtrados.append(movimiento)
            movimientos = movimientos_filtrados
        except ValueError:
            pass  # Si id_articulo no es un número válido, ignorar

    # Aplicar filtros por fecha (NUEVO)
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            movimientos = [m for m in movimientos if m['fecha_movimiento'] >= fecha_desde_dt]
        except ValueError:
            pass

    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Añadir un día para incluir la fecha hasta
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            movimientos = [m for m in movimientos if m['fecha_movimiento'] <= fecha_hasta_dt]
        except ValueError:
            pass

    # Obtener artículos para el dropdown (NUEVO)
    articulos = articulo_model.get_all_articulos()

    # Aplicar paginación
    paginator = Paginator(movimientos, default_per_page=10)

    return render_template(
        'movimientos/salidas/list.html',
        movimientos=paginator.get_items(),
        pagination=paginator.get_pagination_data(),
        search=search,
        articulos=articulos,  # NUEVO: pasar artículos al template
        id_articulo=id_articulo,  # NUEVO: mantener el artículo seleccionado
        fecha_desde=fecha_desde,  # NUEVO: mantener fecha desde
        fecha_hasta=fecha_hasta   # NUEVO: mantener fecha hasta
    )


@movimientos_bp.route('/entradas/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def add_entrada():
    """Crea un nuevo movimiento de entrada - VERSIÓN TEMPORAL CORREGIDA"""
    if request.method == 'POST':
        # Obtener datos del formulario
        fecha_movimiento = request.form.get('fecha_movimiento')
        id_almacen = int(request.form.get('id_almacen'))
        id_tipo_movimiento = int(request.form.get('id_tipo_movimiento'))
        observacion = request.form.get('observacion')
        id_proveedor = request.form.get('id_proveedor')
        id_proveedor = int(id_proveedor) if id_proveedor else None
        id_usuario = session.get('user_id')

        # ✅ CORREGIDO: Guardar en SESIÓN en lugar de BD
        movimiento_temporal = {
            'fecha_movimiento': fecha_movimiento,
            'id_almacen': id_almacen,
            'id_tipo_movimiento': id_tipo_movimiento,
            'observacion': observacion,
            'id_proveedor': id_proveedor,
            'id_usuario': id_usuario,
            'es_entrada': True,
            'detalle': [],  # Lista para artículos
            'timestamp': datetime.now().isoformat()
        }

        # Guardar en sesión
        session['movimiento_temporal'] = movimiento_temporal
        session.modified = True

        flash('✅ Movimiento preparado. Ahora agregue artículos y luego PROCESE para guardar.', 'success')
        return redirect(url_for('movimientos_bp.detalle_movimiento_temporal'))

    tipos_movimiento = tipo_movimiento_model.get_tipos_entrada()
    almacenes = almacen_model.get_all_almacenes()
    proveedores = proveedor_model.get_all_proveedores()

    return render_template('movimientos/entradas/add.html',
                           tipos_movimiento=tipos_movimiento,
                           almacenes=almacenes,
                           proveedores=proveedores,
                           fecha_hoy=datetime.now().strftime('%Y-%m-%dT%H:%M'))


@movimientos_bp.route('/salidas/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def add_salida():
    """Crea un nuevo movimiento de salida - VERSIÓN TEMPORAL CORREGIDA"""
    if request.method == 'POST':
        # Obtener datos del formulario
        fecha_movimiento = request.form.get('fecha_movimiento')
        id_almacen = int(request.form.get('id_almacen'))
        id_tipo_movimiento = int(request.form.get('id_tipo_movimiento'))
        observacion = request.form.get('observacion')
        id_usuario = session.get('user_id')

        # ✅ CORREGIDO: Guardar en SESIÓN en lugar de BD
        movimiento_temporal = {
            'fecha_movimiento': fecha_movimiento,
            'id_almacen': id_almacen,
            'id_tipo_movimiento': id_tipo_movimiento,
            'observacion': observacion,
            'id_usuario': id_usuario,
            'es_entrada': False,
            'detalle': [],  # Lista para artículos
            'timestamp': datetime.now().isoformat()
        }

        # Guardar en sesión
        session['movimiento_temporal'] = movimiento_temporal
        session.modified = True

        flash('✅ Movimiento preparado. Ahora agregue artículos y luego PROCESE para guardar.', 'success')
        return redirect(url_for('movimientos_bp.detalle_movimiento_temporal'))

    tipos_movimiento = tipo_movimiento_model.get_tipos_salida()
    almacenes = almacen_model.get_all_almacenes()

    return render_template('movimientos/salidas/add.html',
                           tipos_movimiento=tipos_movimiento,
                           almacenes=almacenes,
                           fecha_hoy=datetime.now().strftime('%Y-%m-%dT%H:%M'))


@movimientos_bp.route('/detalle-temporal')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def detalle_movimiento_temporal():
    """Muestra el detalle del movimiento temporal (sin guardar en BD)"""
    movimiento_temporal = session.get('movimiento_temporal')

    if not movimiento_temporal:
        flash('No hay movimiento en proceso. Cree un movimiento primero.', 'error')
        return redirect(url_for('movimientos_bp.list_entradas'))

    # Obtener nombres para mostrar
    almacen = almacen_model.get_almacen_by_id(movimiento_temporal['id_almacen'])
    tipo_movimiento = tipo_movimiento_model.get_tipo_movimiento_by_id(movimiento_temporal['id_tipo_movimiento'])

    movimiento_temporal['almacen_nombre'] = almacen['nombre'] if almacen else 'N/A'
    movimiento_temporal['tipo_movimiento_nombre'] = tipo_movimiento['nombre'] if tipo_movimiento else 'N/A'

    if movimiento_temporal.get('id_proveedor'):
        proveedor = proveedor_model.get_proveedor_by_id(movimiento_temporal['id_proveedor'])
        # ✅ CORREGIDO: Usar 'razon_social' en lugar de 'nombre'
        movimiento_temporal['proveedor_nombre'] = proveedor['razon_social'] if proveedor else 'N/A'

    articulos = articulo_model.get_all_articulos()

    # Calcular totales
    total_cantidad = sum(item['cantidad'] for item in movimiento_temporal['detalle'])
    total_valor = sum(item['cantidad'] * item['costo_unitario'] for item in movimiento_temporal['detalle'])

    return render_template('movimientos/detalle_temporal.html',
                           movimiento=movimiento_temporal,
                           articulos=articulos,
                           total_cantidad=total_cantidad,
                           total_valor=total_valor)


@movimientos_bp.route('/agregar_articulo_temporal', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def agregar_articulo_temporal():
    """Agrega un artículo al movimiento temporal"""
    try:
        movimiento_temporal = session.get('movimiento_temporal')
        if not movimiento_temporal:
            return jsonify({'success': False, 'message': 'No hay movimiento en proceso'})

        id_articulo = int(request.form.get('id_articulo'))
        cantidad = int(request.form.get('cantidad'))
        costo_unitario = float(request.form.get('costo_unitario'))

        # Obtener información del artículo
        articulo = articulo_model.get_articulo_by_id(id_articulo)
        if not articulo:
            return jsonify({'success': False, 'message': 'Artículo no encontrado'})

        # Agregar al detalle temporal
        nuevo_item = {
            'id_articulo': id_articulo,
            'articulo_nombre': articulo['nombre'],
            'codigo': articulo['codigo'],
            'cantidad': cantidad,
            'costo_unitario': costo_unitario,
            'unidad_abreviatura': articulo.get('unidad_abreviatura', 'UND')
        }

        movimiento_temporal['detalle'].append(nuevo_item)
        session['movimiento_temporal'] = movimiento_temporal
        session.modified = True

        return jsonify({'success': True, 'message': 'Artículo agregado al movimiento'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@movimientos_bp.route('/procesar-temporal', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def procesar_movimiento_temporal():
    """Procesa el movimiento temporal y lo guarda en BD"""
    movimiento_temporal = session.get('movimiento_temporal')

    if not movimiento_temporal or not movimiento_temporal['detalle']:
        flash('No hay movimiento para procesar o no tiene artículos.', 'error')
        return redirect(url_for('movimientos_bp.detalle_movimiento_temporal'))

    try:
        # ✅ Crear movimiento en BD
        id_movimiento = movimiento_model.create_movimiento(
            movimiento_temporal['fecha_movimiento'],
            movimiento_temporal['id_almacen'],
            movimiento_temporal['id_tipo_movimiento'],
            movimiento_temporal['observacion'],
            movimiento_temporal['id_usuario'],
            movimiento_temporal.get('id_proveedor')
        )

        print(f"🔍 DEBUG: ID Movimiento creado = {id_movimiento}")

        if not id_movimiento:
            flash('Error al crear movimiento en BD.', 'error')
            return redirect(url_for('movimientos_bp.detalle_movimiento_temporal'))

        # ✅ AGREGAR DETALLES CON PRECIO_VENTA Y es_entrada
        for item in movimiento_temporal['detalle']:
            print(f"🔍 DEBUG: Agregando artículo {item}")

            # Determinar precio_venta según tipo de movimiento
            if movimiento_temporal['es_entrada']:
                # Para entradas, precio_venta = costo_unitario
                precio_venta = item['costo_unitario']
            else:
                # Para salidas, usar precio_venta del artículo
                articulo_info = articulo_model.get_articulo_by_id(item['id_articulo'])
                precio_venta = articulo_info['precio_venta'] if articulo_info else item['costo_unitario']

            # ✅ LLAMAR CORRECTAMENTE CON TODOS LOS PARÁMETROS
            success = movimiento_model.agregar_detalle_movimiento(
                id_movimiento,
                item['id_articulo'],
                item['cantidad'],
                item['costo_unitario'],
                precio_venta,
                movimiento_temporal['es_entrada']  # ← NUEVO PARÁMETRO
            )

            if not success:
                print(f"❌ Error al agregar artículo {item['id_articulo']}")
                flash(f'Error al agregar artículo {item["articulo_nombre"]}', 'error')

        # Procesar movimiento (actualizar stock)
        if movimiento_model.actualizar_stock(id_movimiento):
            # Limpiar sesión
            session.pop('movimiento_temporal', None)

            tipo = "entrada" if movimiento_temporal['es_entrada'] else "salida"
            flash(f'✅ Movimiento de {tipo} procesado y guardado exitosamente.', 'success')
            return redirect(url_for('movimientos_bp.detalle_movimiento', id_movimiento=id_movimiento))
        else:
            flash('Error al procesar movimiento.', 'error')
            return redirect(url_for('movimientos_bp.detalle_movimiento_temporal'))

    except Exception as e:
        print(f"❌ ERROR en procesar-temporal: {str(e)}")
        flash(f'Error al procesar movimiento: {str(e)}', 'error')
        return redirect(url_for('movimientos_bp.detalle_movimiento_temporal'))


@movimientos_bp.route('/cancelar-temporal', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def cancelar_movimiento_temporal():
    """Cancela el movimiento temporal sin guardar en BD"""
    if 'movimiento_temporal' in session:
        session.pop('movimiento_temporal', None)
        flash('Movimiento cancelado exitosamente.', 'info')

    return redirect(url_for('movimientos_bp.list_entradas'))


@movimientos_bp.route('/eliminar-articulo-temporal/<int:index>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def eliminar_articulo_temporal(index):
    """Elimina un artículo del movimiento temporal"""
    movimiento_temporal = session.get('movimiento_temporal')

    if not movimiento_temporal:
        return jsonify({'success': False, 'message': 'No hay movimiento en proceso'})

    try:
        if 0 <= index < len(movimiento_temporal['detalle']):
            movimiento_temporal['detalle'].pop(index)
            session['movimiento_temporal'] = movimiento_temporal
            session.modified = True
            return jsonify({'success': True, 'message': 'Artículo eliminado del movimiento'})
        else:
            return jsonify({'success': False, 'message': 'Índice de artículo inválido'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@movimientos_bp.route('/detalle/<int:id_movimiento>')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def detalle_movimiento(id_movimiento):
    """Muestra el detalle de un movimiento."""
    movimiento = movimiento_model.get_movimiento_by_id(id_movimiento)
    if not movimiento:
        flash('Movimiento no encontrado.', 'error')
        return redirect(url_for('movimientos_bp.list_entradas'))

    detalle = movimiento_model.get_detalle_movimiento(id_movimiento)
    articulos = articulo_model.get_all_articulos()

    # Calcular totales
    # Calcular totales
    total_cantidad = sum(item['cantidad'] for item in detalle)
    # Usar precio_venta para salidas, costo_unitario para entradas
    # En detalle_movimiento - AHORA SÍ FUNCIONARÁ
    total_valor = sum(
        item['cantidad'] * (
            item['precio_venta'] if not movimiento['es_entrada'] else item['costo_unitario']
        ) for item in detalle
    )

    return render_template('movimientos/detalle.html',
                           movimiento=movimiento,
                           detalle=detalle,
                           articulos=articulos,
                           total_cantidad=total_cantidad,
                           total_valor=total_valor)


@movimientos_bp.route('/agregar_articulo', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def agregar_articulo_movimiento():
    """Agrega un artículo al movimiento."""
    try:
        id_movimiento = int(request.form.get('id_movimiento'))
        id_articulo = int(request.form.get('id_articulo'))
        cantidad = int(request.form.get('cantidad'))
        costo_unitario = float(request.form.get('costo_unitario'))

        if movimiento_model.agregar_detalle_movimiento(id_movimiento, id_articulo, cantidad, costo_unitario):
            return jsonify({'success': True, 'message': 'Artículo agregado al movimiento'})
        else:
            return jsonify({'success': False, 'message': 'Error al agregar artículo'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@movimientos_bp.route('/procesar/<int:id_movimiento>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def procesar_movimiento(id_movimiento):
    """Procesa un movimiento y actualiza el stock - VERSIÓN MEJORADA"""
    print(f"🎯 [MANUAL] Procesando movimiento {id_movimiento}")

    # Verificar que el movimiento tenga artículos
    detalle = movimiento_model.get_detalle_movimiento(id_movimiento)
    if not detalle:
        flash('❌ No se puede procesar un movimiento sin artículos.', 'error')
        return redirect(url_for('movimientos_bp.detalle_movimiento', id_movimiento=id_movimiento))

    # Obtener información del movimiento
    movimiento = movimiento_model.get_movimiento_by_id(id_movimiento)
    if not movimiento:
        flash('❌ Movimiento no encontrado.', 'error')
        return redirect(url_for('movimientos_bp.detalle_movimiento', id_movimiento=id_movimiento))

    print(f"🎯 [MANUAL] Movimiento tipo: {'ENTRADA' if movimiento['es_entrada'] else 'SALIDA'}")

    try:
        # ✅ NUEVO: Validar stock para salidas ANTES de procesar
        if not movimiento['es_entrada']:  # Es salida
            for item in detalle:
                stock_actual = movimiento_model.get_stock_articulo(item['id_articulo'])
                if stock_actual < item['cantidad']:
                    flash(f'❌ Stock insuficiente para {item["nombre_articulo"]}. Stock actual: {stock_actual}', 'error')
                    return redirect(url_for('movimientos_bp.detalle_movimiento', id_movimiento=id_movimiento))

        # ✅ CORREGIDO: Procesar movimiento SOLO cuando se confirma
        if movimiento_model.actualizar_stock(id_movimiento):
            tipo = "entrada" if movimiento['es_entrada'] else "salida"
            flash(f'✅ Movimiento de {tipo} procesado exitosamente. Stock actualizado.', 'success')

            # ✅ NUEVO: Registrar en logs
            print(f"✅ [MANUAL] Movimiento {id_movimiento} procesado exitosamente")
        else:
            flash('❌ Error al procesar movimiento. Verifique el stock disponible.', 'error')

    except Exception as e:
        print(f"❌ [MANUAL] Error en procesar_movimiento: {e}")
        flash(f'❌ Error al procesar movimiento: {str(e)}', 'error')

    return redirect(url_for('movimientos_bp.detalle_movimiento', id_movimiento=id_movimiento))


@movimientos_bp.route('/eliminar/<int:id_movimiento>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def eliminar_movimiento(id_movimiento):
    """Elimina un movimiento."""
    if movimiento_model.delete_movimiento(id_movimiento):
        flash('Movimiento eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar movimiento.', 'error')

    # Redirigir a la lista correspondiente
    movimiento = movimiento_model.get_movimiento_by_id(id_movimiento)
    if movimiento and movimiento['es_entrada']:
        return redirect(url_for('movimientos_bp.list_entradas'))
    else:
        return redirect(url_for('movimientos_bp.list_salidas'))


