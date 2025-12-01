# app/controllers/categoria_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.categoria_model import CategoriaModel
from app.controllers.auth_controller import login_required, role_required

categorias_bp = Blueprint('categorias_bp', __name__)
categoria_model = CategoriaModel()


@categorias_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO']) # Ajusta los roles de acceso
def list_categorias():
    """Muestra el listado de todas las categorías."""
    categorias = categoria_model.get_all_categorias()
    return render_template('categorias/list.html', categorias=categorias)


@categorias_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_categoria():
    """Permite añadir una nueva categoría."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        if categoria_model.create_categoria(nombre, descripcion):
            flash('Categoría agregada exitosamente.', 'success')
            return redirect(url_for('categorias_bp.list_categorias'))
        else:
            flash('Error al agregar categoría. El nombre de categoría ya existe.', 'error')

    return render_template('categorias/add.html')


@categorias_bp.route('/edit/<int:id_categoria>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_categoria(id_categoria):
    """Permite editar una categoría existente."""
    categoria = categoria_model.get_categoria_by_id(id_categoria)

    if not categoria:
        flash('Categoría no encontrada.', 'error')
        return redirect(url_for('categorias_bp.list_categorias'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        if categoria_model.update_categoria(id_categoria, nombre, descripcion):
            flash('Categoría actualizada exitosamente.', 'success')
            return redirect(url_for('categorias_bp.list_categorias'))
        else:
            flash('Error al actualizar categoría. El nombre de categoría ya existe en otro registro.', 'error')

    return render_template('categorias/edit.html', categoria=categoria)


@categorias_bp.route('/delete/<int:id_categoria>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_categoria(id_categoria):
    """Permite eliminar una categoría."""
    if categoria_model.delete_categoria(id_categoria):
        flash('Categoría eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar categoría. Puede estar siendo usada por algún producto.', 'error')

    return redirect(url_for('categorias_bp.list_categorias'))