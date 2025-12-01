# app/controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user_model import UserModel
from datetime import datetime
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)
user_model = UserModel()

# Función para requerir login (decorador)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # La redirección al login está bien
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

# Función para requerir un rol específico (decorador)
# NOTA: Los roles deben pasarse en MAYÚSCULAS, por ejemplo: role_required(['ADMINISTRADOR', 'ALMACENERO'])
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Asegúrate de que los roles que se verifican son los que están en la DB (MAYÚSCULAS)
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('No tienes permiso para acceder a esta página.', 'error')
                return redirect(url_for('dashboard_bp.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = user_model.get_user_by_username(username)

        # Si el usuario existe y la contraseña es correcta
        if user and user.get('password_hash') and user_model.verify_password(password, user.get('password_hash')):
            session['user_id'] = user.get('id_usuario')
            session['username'] = user.get('nombre_usuario')
            session['user_role'] = user.get('rol') # El modelo retorna el nombre del rol
            user_model.update_last_login(user.get('id_usuario'))
            # Línea eliminada: print("--- LOGIN EXITOSO ---")
            return redirect(url_for('dashboard_bp.dashboard')) # Redirección exitosa
        else:
            # Si el usuario no existe o la contraseña es incorrecta
            flash('Usuario o contraseña incorrectos.', 'error')
            # Línea eliminada: print("--- DEBUG: Fallo en el login. Usuario o contraseña incorrectos. ---")

    return render_template('login.html')

# Versión mejorada de logout
@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Elimina todas las claves de la sesión.
    session.clear()
    return redirect(url_for('auth_bp.login'))