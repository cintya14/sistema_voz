# app/controllers/voice/voice_assistant.py
from flask import Blueprint, request, jsonify, session, render_template
from app.services.voice.intent_detector import IntentDetector
from app.controllers.auth_controller import login_required
from datetime import datetime
from app.services.voice.movement_service import MovementService
from flask import session
# Crear Blueprint
voice_bp = Blueprint('voice_bp', __name__,
                     template_folder='../../views/voice',
                     static_folder='../../static/voice')

# Instancia global del detector
intent_detector = IntentDetector()
movement_service = MovementService()


@voice_bp.route('/interface')
@login_required
def voice_interface():
    """Renderiza la interfaz principal de voz"""
    return render_template('voice_interface.html', now=datetime.now())


@voice_bp.route('/process', methods=['POST'])
@login_required
def process_voice_command():
    """
    Endpoint para procesar comandos de voz/texto
    """
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({
                "error": True,
                "message": "No se recibió comando"
            }), 400

        command_text = data['command'].strip()
        if not command_text:
            return jsonify({
                "error": True,
                "message": "Comando vacío"
            }), 400

        print(f"🔊 Procesando comando: '{command_text}'")

        # Analizar el comando
        analysis = intent_detector.analyze_command(command_text)

        # Agregar metadata
        analysis['comando_original'] = command_text
        analysis['usuario_id'] = session.get('user_id')
        analysis['timestamp'] = datetime.now().isoformat()
        analysis['error'] = False

        print(f"✅ Análisis completado: {analysis['intencion']}")
        if analysis['intencion'] == 'BUSCAR_PRODUCTO':
            print(f"📦 Productos encontrados: {analysis['cantidad_resultados']}")

        return jsonify(analysis)

    except Exception as e:
        print(f"❌ Error en process_voice_command: {e}")
        return jsonify({
            "error": True,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500


@voice_bp.route('/execute', methods=['POST'])
@login_required
def execute_command():
    """Ejecuta una acción confirmada (movimiento) - ✅ ACTUALIZADO"""
    try:
        data = request.get_json()
        if not data or 'action_data' not in data:
            return jsonify({
                "error": True,
                "message": "No se recibieron datos de acción"
            }), 400

        action_data = data['action_data']
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({
                "error": True,
                "message": "Usuario no autenticado"
            }), 401

        intent = action_data.get('intencion')
        producto = action_data.get('producto_seleccionado')
        cantidad = action_data.get('cantidad')

        if not producto or not cantidad:
            return jsonify({
                "error": True,
                "message": "Datos incompletos para ejecutar la acción"
            }), 400

        # ✅ ACTUALIZADO: Ejecutar la acción con observaciones descriptivas
        if intent == 'REGISTRAR_ENTRADA':
            success, message = movement_service.registrar_entrada(
                producto['id_articulo'],
                cantidad,
                user_id,
                observaciones=f"Entrada por voz: {cantidad} {producto['nombre']}"  # ✅ NUEVO PARÁMETRO
            )
        elif intent == 'REGISTRAR_SALIDA':
            success, message = movement_service.registrar_salida(
                producto['id_articulo'],
                cantidad,
                user_id,
                observaciones=f"Salida por voz: {cantidad} {producto['nombre']}"   # ✅ NUEVO PARÁMETRO
            )
        else:
            return jsonify({
                "error": True,
                "message": "Acción no soportada"
            }), 400

        return jsonify({
            "error": not success,
            "message": message,
            "action_executed": True
        })

    except Exception as e:
        print(f"❌ Error en execute_command: {e}")
        return jsonify({
            "error": True,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500


@voice_bp.route('/test-search')
@login_required
def test_search():
    """Endpoint para probar búsqueda de productos"""
    try:
        test_queries = ["hojas A4", "cuadernos", "lápices", "utilies escolares"]
        results = {}

        for query in test_queries:
            productos = intent_detector.product_matcher.buscar_productos(query)
            results[query] = {
                'cantidad': len(productos),
                'productos': productos[:3]  # Mostrar solo 3
            }

        return jsonify({
            "status": "success",
            "results": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500