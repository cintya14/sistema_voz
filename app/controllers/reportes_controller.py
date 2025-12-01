from flask import Blueprint, render_template, request, jsonify, send_file
from app.models.reporte_model import ReporteModel
from app.controllers.auth_controller import login_required, role_required
from app.utils.pdf_generator import generar_pdf
import io
from datetime import datetime

reportes_bp = Blueprint('reportes_bp', __name__)
reporte_model = ReporteModel()


@reportes_bp.route('/')
@login_required
def index_reportes():
    """Página principal de reportes."""
    return render_template('reportes/index.html')


@reportes_bp.route('/kardex')
@login_required
def reporte_kardex():
    """Reporte de Kardex por artículo."""
    articulos = reporte_model.get_articulos_para_reporte()
    almacenes = reporte_model.get_almacenes()
    return render_template('reportes/kardex.html', articulos=articulos, almacenes=almacenes)


@reportes_bp.route('/stock')
@login_required
def reporte_stock():
    """Reporte de stock actual."""
    almacenes = reporte_model.get_almacenes()
    return render_template('reportes/stock.html', almacenes=almacenes)


@reportes_bp.route('/movimientos')
@login_required
def reporte_movimientos():
    """Reporte de movimientos."""
    tipos_movimiento = reporte_model.get_tipos_movimiento()
    almacenes = reporte_model.get_almacenes()
    return render_template('reportes/movimientos.html', tipos_movimiento=tipos_movimiento, almacenes=almacenes)


@reportes_bp.route('/api/kardex')
@login_required
def api_kardex():
    """API para obtener datos del reporte de Kardex."""
    try:
        id_articulo = request.args.get('id_articulo', type=int)
        id_almacen = request.args.get('id_almacen', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        datos = reporte_model.get_kardex_articulo(id_articulo, id_almacen, fecha_desde, fecha_hasta)

        return jsonify({
            'success': True,
            'data': datos,
            'total': len(datos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reportes_bp.route('/api/stock')
@login_required
def api_stock():
    """API para obtener datos del reporte de stock."""
    try:
        id_almacen = request.args.get('id_almacen', type=int)
        stock_minimo = request.args.get('stock_minimo', 'false').lower() == 'true'

        datos = reporte_model.get_stock_almacen(id_almacen, stock_minimo)

        return jsonify({
            'success': True,
            'data': datos,
            'total': len(datos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reportes_bp.route('/api/movimientos')
@login_required
def api_movimientos():
    """API para obtener datos del reporte de movimientos."""
    try:
        id_tipo_movimiento = request.args.get('id_tipo_movimiento', type=int)
        id_almacen = request.args.get('id_almacen', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        datos = reporte_model.get_movimientos_periodo(id_tipo_movimiento, id_almacen, fecha_desde, fecha_hasta)

        return jsonify({
            'success': True,
            'data': datos,
            'total': len(datos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reportes_bp.route('/exportar/pdf')
@login_required
def exportar_pdf():
    """Exporta reporte a PDF."""
    try:
        tipo_reporte = request.args.get('tipo')
        datos = request.args.get('datos', '{}')

        # Generar PDF
        pdf_buffer = generar_pdf(tipo_reporte, datos)

        nombre_archivo = f"reporte_{tipo_reporte}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500