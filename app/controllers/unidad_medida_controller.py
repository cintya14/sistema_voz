# app/controllers/unidad_medida_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.unidad_medida_model import UnidadMedidaModel
from app.controllers.auth_controller import login_required, role_required

unidades_medida_bp = Blueprint('unidades_medida_bp', __name__)
unidad_medida_model = UnidadMedidaModel()


@unidades_medida_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO']) # Ajusta los roles de acceso
def list_unidades_medida():
    """Muestra el listado de todas las unidades de medida."""
    unidades = unidad_medida_model.get_all_unidades_medida()
    return render_template('unidades_medida/list.html', unidades=unidades)


@unidades_medida_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_unidad_medida():
    """Permite añadir una nueva unidad de medida."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        abreviatura = request.form.get('abreviatura')

        if unidad_medida_model.create_unidad_medida(nombre, abreviatura):
            flash('Unidad de medida agregada exitosamente.', 'success')
            return redirect(url_for('unidades_medida_bp.list_unidades_medida'))
        else:
            flash('Error al agregar unidad de medida. El nombre o abreviatura ya existen.', 'error')

    return render_template('unidades_medida/add.html')


@unidades_medida_bp.route('/edit/<int:id_unidad_medida>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_unidad_medida(id_unidad_medida):
    """Permite editar una unidad de medida existente."""
    unidad = unidad_medida_model.get_unidad_medida_by_id(id_unidad_medida)

    if not unidad:
        flash('Unidad de medida no encontrada.', 'error')
        return redirect(url_for('unidades_medida_bp.list_unidades_medida'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        abreviatura = request.form.get('abreviatura')

        if unidad_medida_model.update_unidad_medida(id_unidad_medida, nombre, abreviatura):
            flash('Unidad de medida actualizada exitosamente.', 'success')
            return redirect(url_for('unidades_medida_bp.list_unidades_medida'))
        else:
            flash('Error al actualizar unidad de medida. El nombre o abreviatura ya existen en otro registro.', 'error')

    return render_template('unidades_medida/edit.html', unidad=unidad)


@unidades_medida_bp.route('/delete/<int:id_unidad_medida>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_unidad_medida(id_unidad_medida):
    """Permite eliminar una unidad de medida."""
    if unidad_medida_model.delete_unidad_medida(id_unidad_medida):
        flash('Unidad de medida eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar unidad de medida. Puede estar siendo usada por un producto.', 'error')

    return redirect(url_for('unidades_medida_bp.list_unidades_medida'))