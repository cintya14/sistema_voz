from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.almacen_model import AlmacenModel
from app.controllers.auth_controller import login_required, role_required

almacenes_bp = Blueprint('almacenes_bp', __name__)
almacen_model = AlmacenModel()

@almacenes_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_almacenes():
    """Muestra el listado de todos los almacenes."""
    almacenes = almacen_model.get_all_almacenes()
    return render_template('almacenes/list.html', almacenes=almacenes)

@almacenes_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_almacen():
    """Permite añadir un nuevo almacén."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        es_principal = 1 if request.form.get('es_principal') else 0

        if almacen_model.create_almacen(nombre, direccion, es_principal):
            flash('Almacén agregado exitosamente.', 'success')
            return redirect(url_for('almacenes_bp.list_almacenes'))
        else:
            flash('Error al agregar almacén. El nombre del almacén ya existe.', 'error')

    return render_template('almacenes/add.html')

@almacenes_bp.route('/edit/<int:id_almacen>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_almacen(id_almacen):
    """Permite editar un almacén existente."""
    almacen = almacen_model.get_almacen_by_id(id_almacen)

    if not almacen:
        flash('Almacén no encontrado.', 'error')
        return redirect(url_for('almacenes_bp.list_almacenes'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        es_principal = 1 if request.form.get('es_principal') else 0

        if almacen_model.update_almacen(id_almacen, nombre, direccion, es_principal):
            flash('Almacén actualizado exitosamente.', 'success')
            return redirect(url_for('almacenes_bp.list_almacenes'))
        else:
            flash('Error al actualizar almacén. El nombre del almacén ya existe en otro registro.', 'error')

    return render_template('almacenes/edit.html', almacen=almacen)

@almacenes_bp.route('/delete/<int:id_almacen>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_almacen(id_almacen):
    """Permite eliminar un almacén."""
    if almacen_model.delete_almacen(id_almacen):
        flash('Almacén eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar almacén. Puede estar siendo usado en algún movimiento.', 'error')

    return redirect(url_for('almacenes_bp.list_almacenes'))