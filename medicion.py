from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def generar_pdf_con_regla(input_pdf_path, output_pdf_path):
    # 1. Crear el overlay de la regla
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Configurar estilo de la regla (gris claro y líneas punteadas)
    can.setStrokeColorRGB(0.8, 0.8, 0.8)
    can.setFont("Helvetica", 7)
    
    # Dibujar líneas verticales (Eje X) cada 20 puntos
    for x in range(0, 612, 20):
        can.line(x, 0, x, 792)
        if x % 40 == 0: # Poner el número cada 40 puntos
            can.drawString(x + 2, 10, str(x))
            can.drawString(x + 2, 780, str(x))

    # Dibujar líneas horizontales (Eje Y) cada 20 puntos
    for y in range(0, 792, 20):
        can.line(0, y, 612, y)
        if y % 40 == 0:
            can.drawString(10, y + 2, str(y))
            can.drawString(590, y + 2, str(y))

    can.save()
    packet.seek(0)
    
    # 2. Mezclar la regla con el PDF original
    regla_reader = PdfReader(packet)
    regla_pagina = regla_reader.pages[0]
    
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for pagina in reader.pages:
        # Fusionar la regla sobre cada página existente
        pagina.merge_page(regla_pagina)
        writer.add_page(pagina)

    # 3. Guardar el resultado
    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"¡Éxito! Archivo generado: {output_pdf_path}")

# Ejecutar (Asegúrate de que el nombre del archivo coincida)
generar_pdf_con_regla("plantilla_ministerio.pdf", "plantilla_con_regla.pdf")