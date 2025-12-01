from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.serie_documento_model import SerieDocumentoModel
from app.models.tipo_documento_model import TipoDocumentoModel
from app.controllers.auth_controller import login_required, role_required

series_documento_bp = Blueprint('series_documento_bp', __name__)
serie_documento_model = SerieDocumentoModel()
tipo_documento_model = TipoDocumentoModel()

@series_documento_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'GERENTE'])
def list_series_documento():
    """Muestra el listado de todas las series de documento."""
    series_documento = serie_documento_model.get_all_series_documento()
    return render_template('series_documento/list.html', series_documento=series_documento)

@series_documento_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_serie_documento():
    """Permite añadir una nueva serie de documento."""
    tipos_documento = tipo_documento_model.get_all_tipos_documento()

    if request.method == 'POST':
        id_tipo_documento = int(request.form.get('id_tipo_documento'))
        serie = request.form.get('serie')
        correlativo_actual = int(request.form.get('correlativo_actual', 0))

        if serie_documento_model.create_serie_documento(id_tipo_documento, serie, correlativo_actual):
            flash('Serie de documento agregada exitosamente.', 'success')
            return redirect(url_for('series_documento_bp.list_series_documento'))
        else:
            flash('Error al agregar serie de documento. La serie ya existe para este tipo de documento.', 'error')

    return render_template('series_documento/add.html', tipos_documento=tipos_documento)

@series_documento_bp.route('/edit/<int:id_serie>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_serie_documento(id_serie):
    """Permite editar una serie de documento existente."""
    serie_documento = serie_documento_model.get_serie_documento_by_id(id_serie)
    tipos_documento = tipo_documento_model.get_all_tipos_documento()

    if not serie_documento:
        flash('Serie de documento no encontrada.', 'error')
        return redirect(url_for('series_documento_bp.list_series_documento'))

    if request.method == 'POST':
        id_tipo_documento = int(request.form.get('id_tipo_documento'))
        serie = request.form.get('serie')
        correlativo_actual = int(request.form.get('correlativo_actual', 0))

        if serie_documento_model.update_serie_documento(id_serie, id_tipo_documento, serie, correlativo_actual):
            flash('Serie de documento actualizada exitosamente.', 'success')
            return redirect(url_for('series_documento_bp.list_series_documento'))
        else:
            flash('Error al actualizar serie de documento. La serie ya existe para este tipo de documento.', 'error')

    return render_template('series_documento/edit.html', serie_documento=serie_documento, tipos_documento=tipos_documento)

@series_documento_bp.route('/delete/<int:id_serie>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_serie_documento(id_serie):
    """Permite eliminar una serie de documento."""
    if serie_documento_model.delete_serie_documento(id_serie):
        flash('Serie de documento eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar serie de documento. Puede estar siendo usada en documentos.', 'error')

    return redirect(url_for('series_documento_bp.list_series_documento'))