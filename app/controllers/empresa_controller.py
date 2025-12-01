from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.empresa_model import EmpresaModel
from app.models.moneda_model import MonedaModel
from app.models.igv_model import IgvModel
from app.controllers.auth_controller import login_required, role_required

empresa_bp = Blueprint('empresa_bp', __name__)

# Inicializar modelos
empresa_model = EmpresaModel()
moneda_model = MonedaModel()
igv_model = IgvModel()


@empresa_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR'])
def view_empresa():
    """Muestra la información completa de la empresa con todas las configuraciones."""
    empresa = empresa_model.get_empresa()
    monedas = moneda_model.get_all_monedas()
    tasas_igv = igv_model.get_all_igv()
    tasa_actual = igv_model.get_igv_actual()

    return render_template('empresa/view.html',
                           empresa=empresa,
                           monedas=monedas,
                           tasas_igv=tasas_igv,
                           tasa_actual=tasa_actual)


@empresa_bp.route('/edit', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_empresa():
    """Permite editar la información básica de la empresa."""
    empresa = empresa_model.get_empresa()
    monedas = moneda_model.get_all_monedas()

    if request.method == 'POST':
        razon_social = request.form.get('razon_social')
        ruc = request.form.get('ruc')
        direccion = request.form.get('direccion')
        id_moneda_base = int(request.form.get('id_moneda_base'))

        if empresa:
            # Actualizar empresa existente
            if empresa_model.update_empresa(razon_social, ruc, direccion, id_moneda_base):
                flash('Información de la empresa actualizada exitosamente.', 'success')
                return redirect(url_for('empresa_bp.view_empresa'))
            else:
                flash('Error al actualizar la información de la empresa.', 'error')
        else:
            # Crear nueva empresa
            if empresa_model.create_empresa(razon_social, ruc, direccion, id_moneda_base):
                flash('Información de la empresa creada exitosamente.', 'success')
                return redirect(url_for('empresa_bp.view_empresa'))
            else:
                flash('Error al crear la información de la empresa.', 'error')

    return render_template('empresa/edit.html', empresa=empresa, monedas=monedas)


@empresa_bp.route('/igv/add', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_igv_empresa():
    """Añade una nueva tasa de IGV desde la vista de empresa."""
    porcentaje = float(request.form.get('porcentaje'))
    descripcion = request.form.get('descripcion', '')
    fecha_inicio = request.form.get('fecha_inicio')

    if igv_model.create_igv(porcentaje, descripcion, fecha_inicio):
        flash('Tasa de IGV agregada exitosamente.', 'success')
    else:
        flash('Error al agregar tasa de IGV.', 'error')

    return redirect(url_for('empresa_bp.view_empresa'))


@empresa_bp.route('/igv/delete/<int:id_igv>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_igv_empresa(id_igv):
    """Elimina una tasa de IGV desde la vista de empresa."""
    if igv_model.delete_igv(id_igv):
        flash('Tasa de IGV eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar tasa de IGV.', 'error')

    return redirect(url_for('empresa_bp.view_empresa'))


@empresa_bp.route('/moneda/add', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_moneda_empresa():
    """Añade una nueva moneda desde la vista de empresa."""
    nombre = request.form.get('nombre')
    simbolo = request.form.get('simbolo')
    codigo_iso = request.form.get('codigo_iso')

    if moneda_model.create_moneda(nombre, simbolo, codigo_iso):
        flash('Moneda agregada exitosamente.', 'success')
    else:
        flash('Error al agregar moneda. El código ISO o nombre ya existe.', 'error')

    return redirect(url_for('empresa_bp.view_empresa'))


@empresa_bp.route('/moneda/delete/<int:id_moneda>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_moneda_empresa(id_moneda):
    """Elimina una moneda desde la vista de empresa."""
    if moneda_model.delete_moneda(id_moneda):
        flash('Moneda eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar moneda. Puede estar siendo usada en el sistema.', 'error')

    return redirect(url_for('empresa_bp.view_empresa'))