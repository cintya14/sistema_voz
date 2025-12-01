# app/controllers/usuario_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.usuario_model import UsuarioModel
from app.controllers.auth_controller import login_required, role_required

usuarios_bp = Blueprint('usuarios_bp', __name__)
usuario_model = UsuarioModel()


@usuarios_bp.route('/')
@login_required
@role_required(['ADMINISTRADOR', 'GERENTE']) # Roles ajustados para el ejemplo
def list_usuarios():
    usuarios = usuario_model.get_all_usuarios()
    return render_template('usuarios/list.html', usuarios=usuarios)


@usuarios_bp.route('/search')
@login_required
@role_required(['ADMINISTRADOR', 'GERENTE']) # Roles ajustados para el ejemplo
def search_usuarios():
    query_nombre = request.args.get('query_nombre', '')
    query_dni = request.args.get('query_dni', '')

    usuarios = usuario_model.search_usuarios(query_nombre, query_dni)

    return render_template('usuarios/list.html', usuarios=usuarios, query_nombre=query_nombre, query_dni=query_dni)


@usuarios_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def add_usuario():
    roles = usuario_model.get_all_roles()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        nro_documento = request.form.get('nro_documento')
        nombre_usuario = request.form.get('nombre_usuario')
        email = request.form.get('email')
        password = request.form.get('password')
        # Capturamos el id_rol en lugar del nombre del rol
        id_rol = request.form.get('id_rol', type=int)
        estado = request.form.get('estado')

        if not password or not password.strip():
            flash('La contraseña es un campo obligatorio para crear un usuario.', 'error')
            return render_template('usuarios/add.html', roles=roles) # Pasamos roles de nuevo

        if usuario_model.add_usuario(nombre, apellido, nro_documento, nombre_usuario, email, password, id_rol, estado):
            flash('Usuario agregado exitosamente.', 'success')
            return redirect(url_for('usuarios_bp.list_usuarios'))
        else:
            flash('Error al agregar usuario. El DNI o nombre de usuario ya existe.', 'error')

    return render_template('usuarios/add.html', roles=roles)


@usuarios_bp.route('/edit/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def edit_usuario(id_usuario):
    usuario = usuario_model.get_usuario_by_id(id_usuario)
    roles = usuario_model.get_all_roles() # Obtenemos todos los roles

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('usuarios_bp.list_usuarios'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        nro_documento = request.form.get('nro_documento')
        nombre_usuario = request.form.get('nombre_usuario')
        email = request.form.get('email')
        password = request.form.get('password')
        # Capturamos el id_rol en lugar del nombre del rol
        id_rol = request.form.get('id_rol', type=int)
        estado = request.form.get('estado')

        if usuario_model.update_usuario(id_usuario, nombre, apellido, nro_documento, nombre_usuario, email, password,
                                        id_rol, estado):
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('usuarios_bp.list_usuarios'))
        else:
            flash('Error al actualizar usuario. El DNI o nombre de usuario ya existe en otro registro.', 'error')

    return render_template('usuarios/edit.html', usuario=usuario, roles=roles) # Pasamos roles


@usuarios_bp.route('/delete/<int:id_usuario>', methods=['POST'])
@login_required
@role_required(['ADMINISTRADOR'])
def delete_usuario(id_usuario):
    if usuario_model.delete_usuario(id_usuario):
        flash('Usuario eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar usuario.', 'error')

    return redirect(url_for('usuarios_bp.list_usuarios'))