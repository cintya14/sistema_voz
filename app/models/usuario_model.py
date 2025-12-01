# app/models/usuario_model.py
import mysql.connector
from app.database import get_db_connection, close_db_connection
import bcrypt


class UsuarioModel:
    def __init__(self):
        pass

    def get_all_roles(self):
        """Obtiene todos los roles disponibles de la tabla 'rol'."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT id_rol, nombre FROM rol ORDER BY nombre"
            cursor.execute(query)
            roles = cursor.fetchall()
            return roles
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los roles: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_all_usuarios(self):
        """Obtiene todos los usuarios con el nombre de su rol."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT u.id_usuario, u.nombre, u.apellido, u.nro_documento, u.nombre_usuario, u.email, 
                       r.nombre AS nombre_rol, u.estado, u.fecha_creacion, u.ultimo_login, u.id_rol
                FROM usuario u
                JOIN rol r ON u.id_rol = r.id_rol
                ORDER BY u.apellido, u.nombre
            """
            cursor.execute(query)
            usuarios = cursor.fetchall()
            return usuarios
        except mysql.connector.Error as err:
            print(f"Error al obtener todos los usuarios: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def search_usuarios(self, query_nombre, query_dni):
        """Busca usuarios por nombre/apellido/usuario o DNI con el nombre de su rol."""
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            sql_query = """
                SELECT u.id_usuario, u.nombre, u.apellido, u.nro_documento, u.nombre_usuario, u.email, 
                       r.nombre AS nombre_rol, u.estado, u.fecha_creacion, u.ultimo_login, u.id_rol
                FROM usuario u
                JOIN rol r ON u.id_rol = r.id_rol
                WHERE 1=1
            """
            params = []

            if query_nombre:
                sql_query += " AND (LOWER(u.nombre) LIKE %s OR LOWER(u.apellido) LIKE %s OR LOWER(u.nombre_usuario) LIKE %s)"
                params.extend([f'%{query_nombre.lower()}%', f'%{query_nombre.lower()}%', f'%{query_nombre.lower()}%'])

            if query_dni:
                sql_query += " AND u.nro_documento = %s"
                params.append(query_dni)

            sql_query += " ORDER BY u.apellido, u.nombre"
            cursor.execute(sql_query, params)
            usuarios = cursor.fetchall()
            return usuarios
        except mysql.connector.Error as err:
            print(f"Error al buscar usuarios: {err}")
            return []
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_usuario_by_id(self, id_usuario):
        """Obtiene un usuario por ID."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT u.id_usuario, u.nombre, u.apellido, u.nro_documento, u.nombre_usuario, u.email, 
                       u.id_rol, u.estado, u.fecha_creacion, u.ultimo_login
                FROM usuario u
                WHERE u.id_usuario = %s
            """
            cursor.execute(query, (id_usuario,))
            usuario = cursor.fetchone()
            return usuario
        except mysql.connector.Error as err:
            print(f"Error al obtener usuario por ID: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def get_usuario_by_username(self, nombre_usuario):
        """Obtiene un usuario por nombre de usuario (para login)."""
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT u.*, r.nombre AS nombre_rol FROM usuario u JOIN rol r ON u.id_rol = r.id_rol WHERE nombre_usuario = %s"
            cursor.execute(query, (nombre_usuario,))
            usuario = cursor.fetchone()
            return usuario
        except mysql.connector.Error as err:
            print(f"Error al obtener usuario por nombre de usuario: {err}")
            return None
        finally:
            cursor.close()
            close_db_connection(conn)

    def add_usuario(self, nombre, apellido, nro_documento, nombre_usuario, email, password, id_rol, estado):
        """Agrega un nuevo usuario a la tabla 'usuario'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # 1. Verificar si el nro_documento o nombre_usuario ya existen
            check_query = "SELECT COUNT(*) FROM usuario WHERE nro_documento = %s OR nombre_usuario = %s"
            cursor.execute(check_query, (nro_documento, nombre_usuario))
            if cursor.fetchone()[0] > 0:
                return False # Ya existe un usuario con ese DNI o nombre de usuario

            # 2. Insertar el nuevo usuario
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = "INSERT INTO usuario (nombre, apellido, nro_documento, nombre_usuario, email, password_hash, id_rol, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = (nombre, apellido, nro_documento, nombre_usuario, email, hashed_password.decode('utf-8'), id_rol,
                    estado)
            cursor.execute(query, data)
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error al agregar usuario: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def update_usuario(self, id_usuario, nombre, apellido, nro_documento, nombre_usuario, email, password, id_rol, estado):
        """Actualiza un usuario existente en la tabla 'usuario'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # 1. Verificar si el nro_documento o nombre_usuario ya existen en *otro* usuario
            check_query = "SELECT COUNT(*) FROM usuario WHERE (nro_documento = %s OR nombre_usuario = %s) AND id_usuario != %s"
            cursor.execute(check_query, (nro_documento, nombre_usuario, id_usuario))
            if cursor.fetchone()[0] > 0:
                # Esto es una comprobación un poco ruda. En un caso real, deberías validar cuál de los dos es el duplicado para dar un mensaje más específico.
                print("Error: DNI o nombre de usuario duplicado en otro usuario.")
                return False

            if password and password.strip():
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                query = """
                UPDATE usuario
                SET nombre = %s, apellido = %s, nro_documento = %s, nombre_usuario = %s, email = %s, password_hash = %s, id_rol = %s, estado = %s
                WHERE id_usuario = %s
                """
                data = (nombre, apellido, nro_documento, nombre_usuario, email, hashed_password.decode('utf-8'), id_rol,
                        estado, id_usuario)
            else:
                query = """
                UPDATE usuario
                SET nombre = %s, apellido = %s, nro_documento = %s, nombre_usuario = %s, email = %s, id_rol = %s, estado = %s
                WHERE id_usuario = %s
                """
                data = (nombre, apellido, nro_documento, nombre_usuario, email, id_rol, estado, id_usuario)

            cursor.execute(query, data)
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al actualizar usuario: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

    def delete_usuario(self, id_usuario):
        """Elimina un usuario de la tabla 'usuario'."""
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            query = "DELETE FROM usuario WHERE id_usuario = %s"
            cursor.execute(query, (id_usuario,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar usuario: {err}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)