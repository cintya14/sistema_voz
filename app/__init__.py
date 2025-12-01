# app/__init__.py

from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__, template_folder='views', static_folder='static')
    app.config.from_object(Config)

    # =========================================================================
    # 1. Importar Blueprints (Controladores)
    # =========================================================================

    # Imports de controladores existentes (TODOS)
    from .controllers.auth_controller import auth_bp
    from .controllers.rol_controller import roles_bp
    from .controllers.usuario_controller import usuarios_bp
    from .controllers.modulo_controller import modulos_bp
    from .controllers.unidad_medida_controller import unidades_medida_bp
    from .controllers.categoria_controller import categorias_bp
    from .controllers.marca_controller import marcas_bp
    from .controllers.tipo_documento_controller import tipos_documento_bp
    from .controllers.dashboard_controller import dashboard_bp
    from .controllers.articulo_controller import articulos_bp
    from .controllers.almacen_controller import almacenes_bp
    from .controllers.stock_almacen_controller import stock_almacen_bp
    from .controllers.inventario_inicial_controller import inventario_inicial_bp
    from .controllers.conteo_fisico_controller import conteo_fisico_bp
    from .controllers.kardex_controller import kardex_bp
    from .controllers.movimiento_controller import movimientos_bp
    from .controllers.proveedor_controller import proveedores_bp
    from .controllers.cliente_controller import clientes_bp
    from .controllers.venta_controller import ventas_bp
    from app.controllers.serie_documento_controller import series_documento_bp
    from app.controllers.voice.voice_assistant import voice_bp
    from app.controllers.empresa_controller import empresa_bp
    from app.controllers.reportes_controller import reportes_bp



    # =========================================================================
    # 2. Registrar Blueprints
    # =========================================================================

    # Registro de Blueprints existentes (TODOS)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(roles_bp, url_prefix='/roles')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(modulos_bp, url_prefix='/modulos')
    app.register_blueprint(unidades_medida_bp, url_prefix='/unidades_medida')
    app.register_blueprint(categorias_bp, url_prefix='/categorias')
    app.register_blueprint(marcas_bp, url_prefix='/marcas')
    app.register_blueprint(tipos_documento_bp, url_prefix='/tipos_documento')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(articulos_bp, url_prefix='/articulos')
    app.register_blueprint(almacenes_bp, url_prefix='/almacenes')
    app.register_blueprint(stock_almacen_bp, url_prefix='/stock_almacen')
    app.register_blueprint(inventario_inicial_bp, url_prefix='/inventario_inicial')
    app.register_blueprint(conteo_fisico_bp, url_prefix='/conteo_fisico')
    app.register_blueprint(kardex_bp, url_prefix='/kardex')
    app.register_blueprint(movimientos_bp, url_prefix='/movimientos')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(series_documento_bp, url_prefix='/series_documento')
    app.register_blueprint(voice_bp, url_prefix='/voice')
    app.register_blueprint(empresa_bp, url_prefix='/empresa')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')

    # Ruta principal
    @app.route('/')
    def index():
        return "Bienvenido al Sistema de Inventarios."

    return app
