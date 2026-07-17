from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter
import io


def dibujar_guia(can):
        can.setFont("Helvetica", 7)
        can.setStrokeColorRGB(0.8, 0.8, 0.8) # Gris claro
        for x in range(0, 612, 50):
            can.line(x, 0, x, 792)
            can.drawString(x, 10, str(x))
        for y in range(0, 792, 50):
            can.line(0, y, 612, y)
            can.drawString(10, y, str(y))


# Coordenadas aproximadas para un PDF tamaño Carta (Letter: 612 x 792 pts)
# Coordenadas exactas para la Página 1 (Letter size)
COORD_P1 = {
    # 1.1 Tratamiento de datos
    "tratamiento_si": (513, 483),
    "tratamiento_no": (513, 436),

    # 2.1 Identificación de situaciones
    "situacion_fisica": (327, 334),
    "situacion_psico": (327, 319),
    "situacion_emergencia": (327, 305),
    "situacion_no_aplica": (327, 291),

    # 2.2 Datos generales
    "departamento": (124, 245),
    "uzpe": (486, 245),
    "municipio": (197, 208),
    
    # 6. Área de ubicación (Checkboxes)
    "area_urbana": (225, 191),
    "area_rural": (347, 191),
    "area_centro_poblado": (469, 191),
    
    "territorio": (110, 175),
    "microterritorio": (500, 175),
    "corregimiento_barrio": (110, 159),

    # 2.3 Detalles del Equipo
    "id_equipo": (230, 95),
    "prestador_primario": (310, 80),
}




app = Flask(__name__)


def crear_overlay(datos):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 10) # Negrita para que se vea mejor

    # --- TEXTO ---
    for campo in ["departamento", "uzpe", "municipio", "territorio", "microterritorio", "corregimiento_barrio", "id_equipo", "prestador_primario"]:
        if campo in COORD_P1:
            x, y = COORD_P1[campo]
            can.drawString(x, y, datos.get(campo, '').upper())

    # --- RADIOS / CHECKBOXES (Marcar con X) ---
    # Tratamiento de datos
    if datos.get('tratamiento_datos') == 'SI':
        can.drawString(*COORD_P1["tratamiento_si"], "X")
    elif datos.get('tratamiento_datos') == 'NO':
        can.drawString(*COORD_P1["tratamiento_no"], "X")

    # Situaciones de vida
    situacion = datos.get('situacion_vida')
    if situacion == 'Fisica': can.drawString(*COORD_P1["situacion_fisica"], "X")
    elif situacion == 'Psicologica': can.drawString(*COORD_P1["situacion_psico"], "X")
    elif situacion == 'Emergencia': can.drawString(*COORD_P1["situacion_emergencia"], "X")
    elif situacion == 'No_aplica': can.drawString(*COORD_P1["situacion_no_aplica"], "X")

    # Área de ubicación
    area = datos.get('area_ubicacion')
    if area == 'Urbana': can.drawString(*COORD_P1["area_urbana"], "X")
    elif area == 'Rural': can.drawString(*COORD_P1["area_rural"], "X")
    elif area == 'Centro_poblado': can.drawString(*COORD_P1["area_centro_poblado"], "X")

    can.save()
    packet.seek(0)
    return packet

@app.route('/')
def index():
    return render_template('formulario.html') # El HTML que hicimos antes

@app.route('/generar', methods=['POST'])
def generar():
    # Recibimos los datos del formulario web
    datos = request.form.to_dict()
    # Para los integrantes dinámicos, procesamos las listas
    nombres = request.form.getlist('m_nombre[]')
    
    # 1. Crear el overlay con los datos
    overlay_packet = crear_overlay(datos)
    
    # 2. Leer el PDF original (Plantilla)
    # Debes tener el archivo "plantilla_ministerio.pdf" en la carpeta
    ruta_plantilla = "plantilla_ministerio.pdf"
    reader = PdfReader(ruta_plantilla)
    writer = PdfWriter()
    
    # 3. Fusionar
    overlay_pdf = PdfReader(overlay_packet)
    
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        # Fusionar solo si hay datos para esa página
        if i == 0: # Ejemplo: solo la primera página por ahora
            page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)
    
    # 4. Guardar resultado
    output_path = "Formulario_Final.pdf"
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
        
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)