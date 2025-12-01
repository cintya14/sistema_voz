from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.proveedor_model import ProveedorModel
from app.controllers.auth_controller import login_required, role_required

proveedores_bp = Blueprint('proveedores_bp', __name__)
proveedor_model = ProveedorModel()

@proveedores_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'ALMACENERO'])
def list_proveedores():
    """Muestra el listado de todos los proveedores."""
    proveedores = proveedor_model.get_all_proveedores()
    return render_template('proveedores/list.html', proveedores=proveedores)

@proveedores_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_proveedor():
    """Permite añadir un nuevo proveedor."""
    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        razon_social = request.form.get('razon_social')
        nombre_contacto = request.form.get('nombre_contacto')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')

        if proveedor_model.create_proveedor(tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo):
            flash('Proveedor agregado exitosamente.', 'success')
            return redirect(url_for('proveedores_bp.list_proveedores'))
        else:
            flash('Error al agregar proveedor. El número de documento ya existe.', 'error')

    return render_template('proveedores/add.html')

@proveedores_bp.route('/edit/<int:id_proveedor>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_proveedor(id_proveedor):
    """Permite editar un proveedor existente."""
    proveedor = proveedor_model.get_proveedor_by_id(id_proveedor)

    if not proveedor:
        flash('Proveedor no encontrado.', 'error')
        return redirect(url_for('proveedores_bp.list_proveedores'))

    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        razon_social = request.form.get('razon_social')
        nombre_contacto = request.form.get('nombre_contacto')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')

        if proveedor_model.update_proveedor(id_proveedor, tipo_documento, numero_documento, razon_social, nombre_contacto, direccion, telefono, correo):
            flash('Proveedor actualizado exitosamente.', 'success')
            return redirect(url_for('proveedores_bp.list_proveedores'))
        else:
            flash('Error al actualizar proveedor. El número de documento ya existe en otro registro.', 'error')

    return render_template('proveedores/edit.html', proveedor=proveedor)

@proveedores_bp.route('/delete/<int:id_proveedor>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_proveedor(id_proveedor):
    """Elimina (desactiva) un proveedor."""
    if proveedor_model.delete_proveedor(id_proveedor):
        flash('Proveedor eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar proveedor.', 'error')

    return redirect(url_for('proveedores_bp.list_proveedores'))

@proveedores_bp.route('/activate/<int:id_proveedor>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def activate_proveedor(id_proveedor):
    """Activa un proveedor."""
    if proveedor_model.activate_proveedor(id_proveedor):
        flash('Proveedor activado exitosamente.', 'success')
    else:
        flash('Error al activar proveedor.', 'error')

    return redirect(url_for('proveedores_bp.list_proveedores'))