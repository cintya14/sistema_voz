from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io
import json
from datetime import datetime


def generar_pdf(tipo_reporte, datos_json):
    """Genera un PDF para el reporte solicitado."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1 * inch)
    elements = []
    styles = getSampleStyleSheet()

    # Estilo para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )

    # Datos del reporte
    datos = json.loads(datos_json)

    if tipo_reporte == 'kardex':
        elements.append(Paragraph("Reporte de Kardex", title_style))
        elements.append(generar_tabla_kardex(datos))

    elif tipo_reporte == 'stock':
        elements.append(Paragraph("Reporte de Stock", title_style))
        elements.append(generar_tabla_stock(datos))

    elif tipo_reporte == 'movimientos':
        elements.append(Paragraph("Reporte de Movimientos", title_style))
        elements.append(generar_tabla_movimientos(datos))

    # Pie de página con fecha de generación
    fecha_generacion = Paragraph(
        f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles['Normal']
    )
    elements.append(Spacer(1, 20))
    elements.append(fecha_generacion)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_tabla_kardex(datos):
    """Genera tabla para reporte de kardex."""
    if not datos:
        return Paragraph("No hay datos para mostrar", getSampleStyleSheet()['Normal'])

    # Encabezados
    headers = ['Fecha', 'Movimiento', 'Documento', 'Entrada', 'Salida', 'Saldo', 'Costo Prom.', 'Valor Saldo']

    # Datos
    table_data = [headers]
    for item in datos:
        row = [
            item['fecha'].strftime('%d/%m/%Y'),
            item['tipo_movimiento'],
            f"{item['tipo_documento']} {item['numero_documento']}",
            str(item['cantidad_entrada']),
            str(item['cantidad_salida']),
            str(item['cantidad_saldo']),
            f"S/ {item['costo_promedio']:.2f}",
            f"S/ {item['valor_saldo']:.2f}"
        ]
        table_data.append(row)

    tabla = Table(table_data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    return tabla


def generar_tabla_stock(datos):
    """Genera tabla para reporte de stock."""
    if not datos:
        return Paragraph("No hay datos para mostrar", getSampleStyleSheet()['Normal'])

    headers = ['Código', 'Artículo', 'Categoría', 'Marca', 'Stock', 'Mínimo', 'Precio Compra', 'Precio Venta']

    table_data = [headers]
    for item in datos:
        # Resaltar stock por debajo del mínimo
        estilo_fila = []
        if item['stock_actual'] <= item['stock_minimo']:
            estilo_fila = ['BACKGROUND', (4, len(table_data)), (4, len(table_data)), colors.red]

        row = [
            item['codigo'],
            item['articulo'],
            item['categoria'] or 'N/A',
            item['marca'] or 'N/A',
            str(item['stock_actual']),
            str(item['stock_minimo']),
            f"S/ {item['precio_compra']:.2f}",
            f"S/ {item['precio_venta']:.2f}"
        ]
        table_data.append(row)

    tabla = Table(table_data, repeatRows=1)
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Aplicar estilos condicionales para stock bajo
    for i, item in enumerate(datos, 1):
        if item['stock_actual'] <= item['stock_minimo']:
            estilo.add('BACKGROUND', (4, i), (4, i), colors.red)
            estilo.add('TEXTCOLOR', (4, i), (4, i), colors.white)

    tabla.setStyle(estilo)
    return tabla


def generar_tabla_movimientos(datos):
    """Genera tabla para reporte de movimientos."""
    if not datos:
        return Paragraph("No hay datos para mostrar", getSampleStyleSheet()['Normal'])

    headers = ['Fecha', 'Tipo', 'Almacén', 'Artículo', 'Cantidad', 'Costo Unit.', 'Total', 'Usuario']

    table_data = [headers]
    for item in datos:
        row = [
            item['fecha_movimiento'].strftime('%d/%m/%Y %H:%M'),
            item['tipo_movimiento'],
            item['almacen'],
            f"{item['codigo']} - {item['articulo']}",
            str(item['cantidad']),
            f"S/ {item['costo_unitario']:.2f}",
            f"S/ {item['total']:.2f}",
            item['usuario']
        ]
        table_data.append(row)

    tabla = Table(table_data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    return tabla