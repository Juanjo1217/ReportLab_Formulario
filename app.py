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
    
    "territorio": (108, 173),
    "microterritorio": (388, 173),
    "corregimiento_barrio": (381, 155),

    # 2.3 Detalles del Equipo
    "id_equipo": (240, 93),
    "prestador_primario": (319, 74),
}

COORD_P2 = {

# Sección 2.4: Detalle de personal y Abordaje

# Opciones para Campo 12 (Tipo de ID):
    "p2_id_tipo_cc": (63, 691),
    "p2_id_tipo_cd": (178, 691),
    "p2_id_tipo_ce": (291, 691),
    "p2_id_tipo_pt": (416, 691),

# Campos de Texto:
    "p2_id_numero": (345, 668),
    "p2_perfil_profesional": (484, 642),
    "p2_codigo_ficha": (147, 625),
    "p2_fecha_ficha": (475, 624),


# Opciones para Campo 17 (Entorno):
    "p2_entorno_hogar": (255, 571),
    "p2_entorno_comunitario": (308, 571),
    "p2_entorno_institucional": (383, 572),
    "p2_entorno_educativo": (457, 572),
    "p2_entorno_laboral": (523, 572),
# Campos de Texto (18 y 19):
    "p2_nombre_institucion": (261, 547),
    "p2_cabeza_familia": (329, 530),
# Opciones para Campo 20 (Jóvenes en Paz):
    "p2_jovenes_paz_si": (433, 513),
    "p2_jovenes_paz_no": (519, 513),

# Sección 2.5: Datos generales de la vivienda

# Campos de Texto:
    "p2_direccion": (114, 467),
    "p2_latitud": (201, 449),
    "p2_longitud": (484, 449),
    "p2_punto_referencia": (230, 431),
    "p2_id_hogar": (188, 413),
    "p2_id_familia": (475, 414),

# Opciones para Campo 27 (Estrato):
    "p2_estrato_bajo_bajo": (229, 396),
    "p2_estrato_bajo": (298, 396),
    "p2_estrato_medio_bajo": (344, 396),
    "p2_estrato_medio": (420, 396),
    "p2_estrato_medio_alto": (467, 396),
    "p2_estrato_alto": (541, 396),

# Campos Numéricos (Texto):
    "p2_num_hogares": (222, 379),
    "p2_num_personas": (465, 379),
    "p2_num_habitaciones": (193, 362),
    "p2_elementos_dormir": (443, 359),
    "p2_personas_habitacion": (184, 345),

# Opciones para Campo 33 (Hacinamiento):
    "p2_hacinamiento_si": (141, 326),
    "p2_hacinamiento_no": (191, 325),

# Sección 3.1: Condiciones del entorno y vivienda

# Opciones para Campo 34 (Tipo de vivienda):
    "p2_tipo_vivienda_casa": (147, 243),
    "p2_tipo_vivienda_apto": (198, 243),
    "p2_tipo_vivienda_cuarto": (281, 243),
    "p2_tipo_vivienda_tradicional_indigena": (365, 243),
    "p2_tipo_vivienda_carpa": (506, 243),
    "p2_tipo_vivienda_tradicional_etnica": (49, 229),
    "p2_tipo_vivienda_contenedor": (171, 229),
    "p2_tipo_vivienda_embarcacion": (249, 229),
    "p2_tipo_vivienda_vagon": (328, 229),
    "p2_tipo_vivienda_refugio": (383, 229),
    "p2_tipo_vivienda_cueva": (473, 229),
    "p2_tipo_vivienda_puente": (530, 229),

# Opciones para Campo 35 (Material de cubierta/techo):
    "p2_techo_concreto": (184, 212),
    "p2_techo_barro": (251, 211),
    "p2_techo_fibrocemento_sin_asbesto": (336, 211),
    "p2_techo_zinc": (466, 211),
    "p2_techo_plastico": (515, 211),
    "p2_techo_fibrocemento_con_asbesto": (183, 197),
    "p2_techo_palma": (374, 197),
    "p2_techo_desechos": (456, 197),

# Opciones para Campo 36 (Riesgo de accidentes - Checkboxes múltiples):
    "p2_riesgo_cortantes": (62, 161),
    "p2_riesgo_quimicos": (62, 147),
    "p2_riesgo_medicamentos": (62, 134),
    "p2_riesgo_velas": (277, 134),
    "p2_riesgo_electricas": (62, 119),
    "p2_riesgo_botones": (62, 105),
    "p2_riesgo_pasillos": (62, 90),
    "p2_riesgo_superficies": (299, 90),
    "p2_riesgo_tanques": (62, 77),
    "p2_riesgo_escaleras": (333, 76),
    "p2_riesgo_ninguno": (474, 76),


}


app = Flask(__name__)


def generar_overlay_p1(datos, width, height):
    """Genera el texto de la página 1 con las medidas exactas de la plantilla"""
    packet = io.BytesIO()
    # Inicializamos el lienzo exactamente con el ancho y alto del PDF original
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    # Dibujar textos
    for campo in ["departamento", "uzpe", "municipio", "territorio", "microterritorio", "corregimiento_barrio", "id_equipo", "prestador_primario"]:
        if campo in COORD_P1:
            x, y = COORD_P1[campo]
            can.drawString(x, y, datos.get(campo, '').upper())

    # Marcar decisiones (X)
    if datos.get('tratamiento_datos') == 'SI': can.drawString(*COORD_P1["tratamiento_si"], "X")
    elif datos.get('tratamiento_datos') == 'NO': can.drawString(*COORD_P1["tratamiento_no"], "X")

    situacion = datos.get('situacion_vida')
    if situacion and f"situacion_{situacion.lower()}" in COORD_P1:
        can.drawString(*COORD_P1[f"situacion_{situacion.lower()}"], "X")

    area = datos.get('area_ubicacion')
    if area and f"area_{area.lower()}" in COORD_P1:
        can.drawString(*COORD_P1[f"area_{area.lower()}"], "X")

    can.save()
    packet.seek(0)
    return packet


def generar_overlay_p2(datos, riesgos, width, height):
    """Genera el texto de la página 2 con las medidas exactas de la plantilla"""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    # 1. Dibujar Textos
    campos_texto_p2 = [
        "p2_id_numero", "p2_perfil_profesional", "p2_codigo_ficha", "p2_fecha_ficha",
        "p2_direccion", "p2_latitud", "p2_longitud", "p2_punto_referencia", 
        "p2_id_hogar", "p2_id_familia", "p2_num_hogares", "p2_num_personas", 
        "p2_num_habitaciones", "p2_personas_habitacion", "p2_elementos_dormir"
    ]
    for campo in campos_texto_p2:
        if campo in COORD_P2:
            x, y = COORD_P2[campo]
            can.drawString(x, y, datos.get(campo, '').upper())

    # 2. Dibujar Opciones de Selección (Radios)
    tipo_id = datos.get('p2_id_tipo')
    key_tipo = f"p2_id_tipo_{str(tipo_id).lower()}"
    if key_tipo in COORD_P2: can.drawString(*COORD_P2[key_tipo], "X")

    entorno = datos.get('p2_entorno')
    key_entorno = f"p2_entorno_{str(entorno).lower()}"
    if key_entorno in COORD_P2: can.drawString(*COORD_P2[key_entorno], "X")

    # 3. Dibujar Checkboxes Múltiples (Riesgos)
    for riesgo in riesgos:
        key_riesgo = f"p2_riesgo_{riesgo.lower()}"
        if key_riesgo in COORD_P2:
            can.drawString(*COORD_P2[key_riesgo], "X")

    can.save()
    packet.seek(0)
    return packet


@app.route('/')
def index():
    return render_template('formulario.html')


@app.route('/generar', methods=['POST'])
def generar():
    form_completo = request.form.to_dict()
    datos_p1 = {k: v for k, v in form_completo.items() if not k.startswith("p2_")}
    datos_p2 = {k: v for k, v in form_completo.items() if k.startswith("p2_")}
    riesgos_p2 = request.form.getlist('p2_riesgos[]')

    try:
        # Abrimos la plantilla del ministerio
        reader = PdfReader("plantilla_ministerio.pdf")
        writer = PdfWriter()
        
        # Procesamos página por página
        for idx in range(len(reader.pages)):
            page = reader.pages[idx]
            
            # Extraemos de forma exacta el ancho y el alto de la página de la plantilla
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            
            # Fusión para la Página 1
            if idx == 0:
                overlay_packet = generar_overlay_p1(datos_p1, width, height)
                overlay_reader = PdfReader(overlay_packet)
                page.merge_page(overlay_reader.pages[0]) # Fusión 1:1 sin deformación
                
            # Fusión para la Página 2
            elif idx == 1:
                overlay_packet = generar_overlay_p2(datos_p2, riesgos_p2, width, height)
                overlay_reader = PdfReader(overlay_packet)
                page.merge_page(overlay_reader.pages[0]) # Fusión 1:1 sin deformación
                
            writer.add_page(page)

        # Generar el archivo de descarga
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(output, as_attachment=True, download_name="APS_Ficha_Oficial.pdf")
        
    except Exception as e:
        return f"Error al procesar el PDF: {e}"

if __name__ == '__main__':
    app.run(debug=True)