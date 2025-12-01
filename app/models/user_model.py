# app/models/user_model.py
import mysql.connector
from mysql.connector import Error # Importar Error para capturar excepciones específicas
from app.database import get_db_connection, close_db_connection
from bcrypt import hashpw, gensalt, checkpw

class UserModel:
    def __init__(self):
        pass # No se necesita inicialización especial aquí

    def create_user(self, nombre_usuario, email, password, id_rol): # Modificado para usar id_rol
        """Crea un nuevo usuario en la base de datos."""
        conn = get_db_connection()
        if conn is None:
            # print("ERROR (UserModel): No se pudo establecer conexión con la base de datos para crear usuario.")
            return False

        cursor = conn.cursor()
        try:
            # Hashear la contraseña antes de almacenarla
            password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
            # print(f"DEBUG (UserModel): Hash generado para '{nombre_usuario}': {password_hash[:30]}...")

            # Modificado: Usar tabla 'usuario' e 'id_rol'
            query = """
            INSERT INTO usuario (nombre_usuario, email, password_hash, id_rol) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (nombre_usuario, email, password_hash, id_rol))
            conn.commit()
            # print(f"DEBUG (UserModel): Usuario '{nombre_usuario}' creado exitosamente con ID: {cursor.lastrowid}")
            return cursor.lastrowid # Devuelve el ID del usuario recién creado
        except Error as err: # Usar 'Error' de mysql.connector
            # print(f"ERROR (UserModel): Error al crear usuario '{nombre_usuario}': {err}")
            conn.rollback()
            return False
        finally:
            if cursor: # Asegurarse de que el cursor existe antes de cerrarlo
                cursor.close()
            close_db_connection(conn)

    def get_user_by_username(self, username):
        """Obtiene un usuario por su nombre de usuario. Retorna un diccionario, incluyendo el nombre del rol."""
        conn = get_db_connection()
        if conn is None:
            # print("ERROR (UserModel): No se pudo establecer conexión con la base de datos para obtener usuario.")
            return None

        cursor = conn.cursor(dictionary=True) # Devuelve resultados como diccionarios
        try:
            # Modificado:
            # 1. Usar tabla 'usuario'.
            # 2. INNER JOIN con 'rol' para obtener el nombre del rol (r.nombre) como 'rol'.
            query = """
            SELECT 
                u.id_usuario, 
                u.nombre_usuario, 
                u.email, 
                u.password_hash, 
                r.nombre AS rol 
            FROM 
                usuario u
            INNER JOIN 
                rol r ON u.id_rol = r.id_rol
            WHERE 
                u.nombre_usuario = %s AND u.estado = 'ACTIVO' 
            """
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            # print(f"DEBUG (UserModel): Datos de usuario '{username}' recuperados: {user}") # Para depuración completa
            return user
        except Error as err: # Usar 'Error' de mysql.connector
            # print(f"ERROR (UserModel): Error al obtener usuario '{username}': {err}")
            return None
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)

    def verify_password(self, plain_password, hashed_password):
        """
        Verifica si una contraseña plana (string) coincide con su hash (string).
        """
        if not plain_password or not hashed_password:
            # print("ADVERTENCIA (UserModel): Contraseña plana o hash vacío/None para verificar.")
            return False
        try:
            # checkpw espera bytes para ambos argumentos
            return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError as e:
            # Esto puede ocurrir si el hash almacenado no es un hash bcrypt válido
            # print(f"ERROR (UserModel): ValueError al verificar hash con bcrypt: {e}")
            # print(f"Hash inválido intentando verificar: '{hashed_password}'")
            return False
        except Exception as e:
            # Captura otras excepciones inesperadas
            # print(f"ERROR (UserModel): Error inesperado al verificar contraseña: {e}")
            return False

    def update_last_login(self, user_id):
        """Actualiza la fecha del último login de un usuario."""
        conn = get_db_connection()
        if conn is None:
            # print("ERROR (UserModel): No se pudo establecer conexión con la base de datos para actualizar login.")
            return False

        cursor = conn.cursor()
        try:
            # Modificado: Usar tabla 'usuario'
            query = "UPDATE usuario SET ultimo_login = NOW() WHERE id_usuario = %s"
            cursor.execute(query, (user_id,))
            conn.commit()
            # print(f"DEBUG (UserModel): Último login actualizado para user_id: {user_id}") # Para depuración
            return True
        except Error as err: # Usar 'Error' de mysql.connector
            # print(f"ERROR (UserModel): Error al actualizar último login para user_id {user_id}: {err}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)