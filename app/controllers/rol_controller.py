# app/controllers/rol_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.rol_model import RolModel
from app.controllers.auth_controller import login_required, role_required

roles_bp = Blueprint('roles_bp', __name__)
rol_model = RolModel()


@roles_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'GERENTE']) # Ajusta los roles según tu lógica de acceso
def list_roles():
    """Muestra el listado de todos los roles."""
    roles = rol_model.get_all_roles()
    return render_template('roles/list.html', roles=roles)


@roles_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_rol():
    """Permite añadir un nuevo rol."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if rol_model.create_rol(nombre):
            flash('Rol agregado exitosamente.', 'success')
            return redirect(url_for('roles_bp.list_roles'))
        else:
            flash('Error al agregar rol. El nombre de rol ya existe o hubo un error en la base de datos.', 'error')

    return render_template('roles/add.html')


@roles_bp.route('/edit/<int:id_rol>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_rol(id_rol):
    """Permite editar un rol existente."""
    rol = rol_model.get_rol_by_id(id_rol)

    if not rol:
        flash('Rol no encontrado.', 'error')
        return redirect(url_for('roles_bp.list_roles'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if rol_model.update_rol(id_rol, nombre):
            flash('Rol actualizado exitosamente.', 'success')
            return redirect(url_for('roles_bp.list_roles'))
        else:
            flash('Error al actualizar rol. El nombre de rol ya existe en otro registro.', 'error')

    return render_template('roles/edit.html', rol=rol)


@roles_bp.route('/delete/<int:id_rol>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_rol(id_rol):
    """Permite eliminar un rol."""
    # Considera la nota de seguridad en el modelo sobre la integridad referencial.
    if rol_model.delete_rol(id_rol):
        flash('Rol eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar rol. Asegúrate de que no tenga usuarios asignados.', 'error')

    return redirect(url_for('roles_bp.list_roles'))