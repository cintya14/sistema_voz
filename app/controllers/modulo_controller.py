# app/controllers/modulo_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.modulo_model import ModuloModel
from app.controllers.auth_controller import login_required, role_required # Asumiendo que tienes un auth_controller

modulos_bp = Blueprint('modulos_bp', __name__)
modulo_model = ModuloModel()


@modulos_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'GERENTE']) # Ajusta los roles según tu lógica de acceso
def list_modulos():
    """Muestra el listado de todos los módulos."""
    modulos = modulo_model.get_all_modulos()
    return render_template('modulos/list.html', modulos=modulos)


@modulos_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_modulo():
    """Permite añadir un nuevo módulo."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if modulo_model.create_modulo(nombre):
            flash('Módulo agregado exitosamente.', 'success')
            return redirect(url_for('modulos_bp.list_modulos'))
        else:
            flash('Error al agregar módulo. El nombre de módulo ya existe o hubo un error en la base de datos.', 'error')

    return render_template('modulos/add.html')


@modulos_bp.route('/edit/<int:id_modulo>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_modulo(id_modulo):
    """Permite editar un módulo existente."""
    modulo = modulo_model.get_modulo_by_id(id_modulo)

    if not modulo:
        flash('Módulo no encontrado.', 'error')
        return redirect(url_for('modulos_bp.list_modulos'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if modulo_model.update_modulo(id_modulo, nombre):
            flash('Módulo actualizado exitosamente.', 'success')
            return redirect(url_for('modulos_bp.list_modulos'))
        else:
            flash('Error al actualizar módulo. El nombre de módulo ya existe en otro registro.', 'error')

    return render_template('modulos/edit.html', modulo=modulo)


@modulos_bp.route('/delete/<int:id_modulo>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_modulo(id_modulo):
    """Permite eliminar un módulo."""
    if modulo_model.delete_modulo(id_modulo):
        flash('Módulo eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar módulo. Asegúrate de que no esté siendo utilizado en otras tablas (ej. permisos).', 'error')

    return redirect(url_for('modulos_bp.list_modulos'))