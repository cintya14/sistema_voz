# app/controllers/tipo_documento_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.tipo_documento_model import TipoDocumentoModel
from app.controllers.auth_controller import login_required, role_required

tipos_documento_bp = Blueprint('tipos_documento_bp', __name__)
tipo_documento_model = TipoDocumentoModel()


@tipos_documento_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'GERENTE']) # Ajusta los roles de acceso
def list_tipos_documento():
    """Muestra el listado de todos los tipos de documento."""
    tipos_documento = tipo_documento_model.get_all_tipos_documento()
    return render_template('tipos_documento/list.html', tipos_documento=tipos_documento)


@tipos_documento_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_tipo_documento():
    """Permite añadir un nuevo tipo de documento."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        codigo_sunat = request.form.get('codigo_sunat')

        if tipo_documento_model.create_tipo_documento(nombre, codigo_sunat):
            flash('Tipo de documento agregado exitosamente.', 'success')
            return redirect(url_for('tipos_documento_bp.list_tipos_documento'))
        else:
            flash('Error al agregar tipo de documento. El nombre o código SUNAT ya existen.', 'error')

    return render_template('tipos_documento/add.html')


@tipos_documento_bp.route('/edit/<int:id_tipo_documento>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_tipo_documento(id_tipo_documento):
    """Permite editar un tipo de documento existente."""
    tipo_documento = tipo_documento_model.get_tipo_documento_by_id(id_tipo_documento)

    if not tipo_documento:
        flash('Tipo de documento no encontrado.', 'error')
        return redirect(url_for('tipos_documento_bp.list_tipos_documento'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        codigo_sunat = request.form.get('codigo_sunat')

        if tipo_documento_model.update_tipo_documento(id_tipo_documento, nombre, codigo_sunat):
            flash('Tipo de documento actualizado exitosamente.', 'success')
            return redirect(url_for('tipos_documento_bp.list_tipos_documento'))
        else:
            flash('Error al actualizar tipo de documento. El nombre o código SUNAT ya existen en otro registro.', 'error')

    return render_template('tipos_documento/edit.html', tipo_documento=tipo_documento)


@tipos_documento_bp.route('/delete/<int:id_tipo_documento>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_tipo_documento(id_tipo_documento):
    """Permite eliminar un tipo de documento."""
    if tipo_documento_model.delete_tipo_documento(id_tipo_documento):
        flash('Tipo de documento eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar tipo de documento. Puede estar siendo usado en clientes o transacciones.', 'error')

    return redirect(url_for('tipos_documento_bp.list_tipos_documento'))