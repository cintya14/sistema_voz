from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.cliente_model import ClienteModel
from app.controllers.auth_controller import login_required, role_required

clientes_bp = Blueprint('clientes_bp', __name__)
cliente_model = ClienteModel()

@clientes_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def list_clientes():
    """Muestra el listado de clientes."""
    clientes = cliente_model.get_all_clientes()
    return render_template('clientes/list.html', clientes=clientes)

@clientes_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def add_cliente():
    """Permite añadir un nuevo cliente."""
    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        nombre_o_razon_social = request.form.get('nombre_o_razon_social')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')

        if cliente_model.create_cliente(tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo):
            flash('Cliente agregado exitosamente.', 'success')
            return redirect(url_for('clientes_bp.list_clientes'))
        else:
            flash('Error al agregar cliente. El número de documento ya existe.', 'error')

    return render_template('clientes/add.html')

@clientes_bp.route('/edit/<int:id_cliente>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR', 'VENTAS'])
def edit_cliente(id_cliente):
    """Permite editar un cliente existente."""
    cliente = cliente_model.get_cliente_by_id(id_cliente)

    if not cliente:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('clientes_bp.list_clientes'))

    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        nombre_o_razon_social = request.form.get('nombre_o_razon_social')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')

        if cliente_model.update_cliente(id_cliente, tipo_documento, numero_documento, nombre_o_razon_social, direccion, telefono, correo):
            flash('Cliente actualizado exitosamente.', 'success')
            return redirect(url_for('clientes_bp.list_clientes'))
        else:
            flash('Error al actualizar cliente. El número de documento ya existe en otro registro.', 'error')

    return render_template('clientes/edit.html', cliente=cliente)

@clientes_bp.route('/delete/<int:id_cliente>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_cliente(id_cliente):
    """Elimina un cliente."""
    if cliente_model.delete_cliente(id_cliente):
        flash('Cliente eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar cliente.', 'error')

    return redirect(url_for('clientes_bp.list_clientes'))