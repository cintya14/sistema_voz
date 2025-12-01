# app/controllers/marca_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.marca_model import MarcaModel
from app.controllers.auth_controller import login_required, role_required

marcas_bp = Blueprint('marcas_bp', __name__)
marca_model = MarcaModel()


@marcas_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO']) # Ajusta los roles de acceso
def list_marcas():
    """Muestra el listado de todas las marcas."""
    marcas = marca_model.get_all_marcas()
    return render_template('marcas/list.html', marcas=marcas)


@marcas_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_marca():
    """Permite añadir una nueva marcas."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        if marca_model.create_marca(nombre, descripcion):
            flash('Marca agregada exitosamente.', 'success')
            return redirect(url_for('marcas_bp.list_marcas'))
        else:
            flash('Error al agregar marcas. El nombre de marcas ya existe.', 'error')

    return render_template('marcas/add.html')


@marcas_bp.route('/edit/<int:id_marca>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_marca(id_marca):
    """Permite editar una marcas existente."""
    marca = marca_model.get_marca_by_id(id_marca)

    if not marca:
        flash('Marca no encontrada.', 'error')
        return redirect(url_for('marcas_bp.list_marcas'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        if marca_model.update_marca(id_marca, nombre, descripcion):
            flash('Marca actualizada exitosamente.', 'success')
            return redirect(url_for('marcas_bp.list_marcas'))
        else:
            flash('Error al actualizar marcas. El nombre de marcas ya existe en otro registro.', 'error')

    return render_template('marcas/edit.html', marca=marca)


@marcas_bp.route('/delete/<int:id_marca>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_marca(id_marca):
    """Permite eliminar una marcas."""
    if marca_model.delete_marca(id_marca):
        flash('Marca eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar marcas. Puede estar siendo usada por algún producto.', 'error')

    return redirect(url_for('marcas_bp.list_marcas'))