from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter, Transformation
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

AJUSTE_MANUAL_X_P1 = 0  # Cambia a positivo para mover a la DERECHA, negativo para mover a la IZQUIERDA
AJUSTE_MANUAL_Y_P1 = 0  # Cambia a positivo para mover hacia ARRIBA, negativo para mover hacia ABAJO

AJUSTE_MANUAL_X_P2 = -3  # Ajuste para la Página 2 (DERECHA/IZQUIERDA)
AJUSTE_MANUAL_Y_P2 = -4  # Ajuste para la Página 2 (ARRIBA/ABAJO)

AJUSTE_MANUAL_X_P3 = -3  # Ajuste para la Página 3 (DERECHA/IZQUIERDA)
AJUSTE_MANUAL_Y_P3 = -4  # Ajuste para la Página 3 (ARRIBA/ABAJO)

AJUSTE_MANUAL_X_P4 = -3  # Ajuste para la Página 4 (DERECHA/IZQUIERDA)
AJUSTE_MANUAL_Y_P4 = -4  # Ajuste para la Página 4 (ARRIBA/ABAJO)

AJUSTE_MANUAL_X_P5 = -3  # Ajuste para la Página 5 (DERECHA/IZQUIERDA)
AJUSTE_MANUAL_Y_P5 = -4  # Ajuste para la Página 5 (ARRIBA/ABAJO)

AJUSTE_MANUAL_X_P6 = -3  # Ajuste para la Página 6
AJUSTE_MANUAL_Y_P6 = -4  

AJUSTE_MANUAL_X_P7 = -3  # Ajuste para la Página 7
AJUSTE_MANUAL_Y_P7 = -4  

AJUSTE_MANUAL_X_P8 = -3  # Ajuste para la Página 8
AJUSTE_MANUAL_Y_P8 = -4

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

COORD_P3 = {
# 3.1 Criaderos
    "p3_criaderos_si": (396, 725),"p3_criaderos_no": (453, 725),"p3_criaderos_no_aplica": (512, 725),

# Campo 38 (Entorno - Checkboxes múltiples):
    "p3_ent_cultivos": (356, 703),"p3_ent_apriscos": (420, 703),"p3_ent_porquerizas": (486, 703),

    "p3_ent_galpones": (64, 689),"p3_ent_baldios": (132, 689),"p3_ent_plagas": (228, 689),"p3_ent_olores": (504, 689),

    "p3_ent_ruidos": (63, 675),"p3_ent_excretas": (215, 675),"p3_ent_rellenos": (402, 675),

    "p3_ent_contaminacion": (63, 660),"p3_ent_rio": (176, 661),"p3_ent_planta": (266, 660),"p3_ent_mineria": (444, 661),

    "p3_ent_industrias": (63, 646),
    
    "p3_ent_canales": (63, 632), "p3_ent_vias": (170, 632), "p3_ent_quemas": (306, 632),

    "p3_ent_alta_tension": (63, 618),"p3_ent_agroquimicos": (286, 617),

    "p3_ent_asbesto": (64, 604),"p3_ent_ninguno": (466, 604),


# Campo 39 (Actividad Económica):
    "p3_act_economica_si": (400, 558), "p3_act_economica_no": (506, 558),


# Campo 40 (Animales - Checkboxes múltiples):
    "p3_ani_perros": (456, 540), "p3_ani_gatos": (524, 540),
# Campo 40 (Animales - Checkboxes múltiples):
    "p3_ani_porcinos": (63, 526), "p3_ani_bovinos": (129, 526), "p3_ani_equinos": (272, 526), "p3_ani_ovinos": (450, 526),
    "p3_ani_aves_prod": (63, 512), "p3_ani_aves_orn": (169, 511), "p3_ani_peces": (278, 512), "p3_ani_cobayos": (420, 512),
    "p3_ani_silvestres": (64, 497), "p3_ani_otro": (175, 497),
    
    "p3_ani_ninguno": (390, 497),
    "p3_num_perros": (196, 480),
    "p3_num_perros_vacuna": (521, 480),
    "p3_num_gatos": (196, 462),
    "p3_num_gatos_vacuna": (521, 462),
    "p3_carnet_si": (396, 445),
    "p3_carnet_no": (452, 445),
    "p3_carnet_no_aplica": (511, 444),
    "p3_agua_esp": (434, 398),

    "p3_agua_esp": (63, 385),
    "p3_agua_veredal": (298, 385),
    "p3_agua_pila": (453, 385),
    "p3_agua_carro": (63, 371),
    "p3_agua_comunitaria": (143, 371),
    "p3_agua_pozo_bomba": (309, 371),
    "p3_agua_pozo_sin_bomba": (407, 371),
    "p3_agua_laguna": (63, 357),
    "p3_agua_rio": (159, 356),
    "p3_agua_manantial": (244, 357),
    "p3_agua_lluvias": (364, 357),
    "p3_agua_aguatero": (448, 357),
    "p3_agua_botella": (434, 400),

    "p3_exc_alcantarillado": (63, 325),
    "p3_exc_letrina": (231, 325),
    "p3_exc_septico": (330, 325),
    "p3_exc_seco": (63, 310),
    "p3_exc_sin_conexion": (196, 310),
    "p3_exc_fuente": (310, 310),
    "p3_exc_abierto": (494, 310),

    "p3_res_alcantarillado": (404, 293),
    "p3_res_septico": (505, 293),
    "p3_res_oxidacion": (64, 278),
    "p3_res_biofiltro": (172, 278),
    "p3_res_fuente": (236, 278),
    "p3_res_abierto": (322, 278),

    "p3_sol_recoleccion": (63, 246),
    "p3_sol_enterramiento": (324, 248),
    "p3_sol_quema": (410, 246),
    "p3_sol_fuente": (63, 232),
    "p3_sol_abierto": (241, 232),

    "p3_fam_nuclear_biparental": (157, 146),
    "p3_fam_nuclear_monoparental": (260, 146),
    "p3_fam_extenso_biparental": (375, 147),
    "p3_fam_extenso_monoparental": (63, 132),
    "p3_fam_compuesto_biparental": (188, 133),
    "p3_fam_compuesto_monoparental": (304, 132),
    "p3_fam_unipersonal": (421, 132),

    "p3_fam_personas": (250, 114),

    "p3_cuidador_si": (488, 96),
    "p3_cuidador_no": (538, 96),

    "p3_zarit_ausencia": (63, 64),
    "p3_zarit_ligera": (264, 64),
    "p3_zarit_intensa": (442, 64),


}

COORD_P4 = {
    "p4_riesgo_convivencia": (63, 707),
    "p4_riesgo_nuevo_integrante": (215, 707),
    "p4_riesgo_ingreso_estudiar": (365, 707),
    "p4_riesgo_perdida_ano": (466, 706),
    "p4_riesgo_embarazo_adolescente": (63, 692),
    "p4_riesgo_independencia_hijos": (224, 692),
    "p4_riesgo_separacion": (376, 693),
    "p4_riesgo_jubilacion": (450, 693),
    "p4_riesgo_duelo": (520, 692),
    "p4_riesgo_desempleo": (63, 678),
    "p4_riesgo_crisis_economica": (248, 678),
    "p4_riesgo_muerte_inesperada": (388, 678),
    "p4_riesgo_migracion": (490, 678),
    "p4_riesgo_enfermedad_terminal": (63, 664),
    "p4_riesgo_accidente_discapacidad": (340, 664),
    "p4_riesgo_antecedentes_suicidio": (63, 649),
    "p4_riesgo_violencia": (373, 650),
    "p4_riesgo_abandono": (63, 636),
    "p4_riesgo_consumo_sustancias": (222, 635),
    "p4_riesgo_trastorno_mental": (62, 622),
    "p4_riesgo_ninguna": (200, 622),

    "p4_vinculo_tension": (62, 564),
    "p4_vinculo_decisiones": (63, 549),
    "p4_vinculo_conflictos": (63, 536),
    "p4_vinculo_comunicacion": (62, 520),
    "p4_vinculo_ninos": (62, 506),
    "p4_vinculo_adultos_mayores": (62, 483),

    "p4_red_protectoras": (54, 449),
    "p4_red_ampliables": (54, 435),
    "p4_red_ninguna": (54, 421),

    "p4_hogar_tratamiento_agua": (62, 389),
    "p4_hogar_ventilacion": (62, 374),
    "p4_hogar_evita_humo": (62, 360),
    "p4_hogar_residuos": (63, 345),
    "p4_hogar_limpieza": (62, 324),
    "p4_hogar_toldillos": (63, 309),
    "p4_hogar_limpieza_entorno": (63, 294),
    "p4_hogar_quimicos_seguros": (62, 280),

}

COORD_MIEMBRO = {

# -------------------------------------------------------------
# PÁGINA 5: IDENTIFICACIÓN Y DATOS SOCIOECONÓMICOS
# -------------------------------------------------------------
# Campos de Texto / Números (Página 5)   
"p5_primer_nombre": (136, 666),
"p5_segundo_nombre": (419, 665),
"p5_primer_apellido": (136, 650),
"p5_segundo_apellido": (419, 649),
"p5_id_numero": (170, 571),
"p5_fecha_nacimiento": (429, 570),
"p5_nacionalidad": (128, 554),
"p5_telefono_1": (135, 453),
"p5_telefono_2": (419, 454),
"p5_ocupacion": (135, 378),
"p5_eapb": (103, 296),
"p5_pueblo_etnico": (252, 128),
"p5_identidad_otro_cual": (159, 504),
"p5_orientacion_otro_cual": (151, 472),
"p5_prot_otro_cual": (141, 208),

"p5_id_tipo_as": (254, 631),
"p5_id_tipo_cc": (390, 631),
"p5_id_tipo_cd": (63, 617),
"p5_id_tipo_ce": (178, 617),
"p5_id_tipo_ms": (302, 617),
"p5_id_tipo_nv": (438, 617),
"p5_id_tipo_pe": (63, 603),
"p5_id_tipo_pt": (235, 603),
"p5_id_tipo_rc": (402, 603),
"p5_id_tipo_ti": (62, 589),
"p5_sexo_hombre": (331, 553),
"p5_sexo_mujer": (395, 553),
"p5_sexo_intersexual": (449, 553),
"p5_genero_femenino": (167, 535),
"p5_genero_masculino": (268, 535),
"p5_identidad_femenino": (178, 516),
"p5_identidad_masculino": (246, 516),
"p5_identidad_transexual": (316, 516),
"p5_identidad_transgenero": (388, 516),
"p5_identidad_no_responde": (467, 516),
"p5_identidad_otro": (70, 503),
"p5_orientacion_hetero": (206, 485),
"p5_orientacion_lesbiana": (292, 485),
"p5_orientacion_gay": (357, 485),
"p5_orientacion_bisexual": (405, 485),
"p5_orientacion_no_responde": (476, 485),
"p5_orientacion_otro": (64, 471),
"p5_rol_resp_economico": (209, 434),
"p5_rol_conyuge": (376, 435),
"p5_rol_hijo": (63, 421),
"p5_rol_hermano": (120, 421),
"p5_rol_padre_madre": (196, 421),
"p5_rol_otros": (282, 421),
"p5_educacion_preescolar": (150, 359),
"p5_educacion_primaria": (222, 359),
"p5_educacion_secundaria": (313, 359),
"p5_educacion_media": (411, 359),
"p5_educacion_media_tecnica": (63, 345),
"p5_educacion_normalista": (226, 345),
"p5_educacion_tecnica_prof": (299, 345),
"p5_educacion_tecnologica": (403, 345),
"p5_educacion_profesional": (482, 345),
"p5_educacion_especializacion": (62, 331),
"p5_educacion_maestria": (150, 331),
"p5_educacion_doctorado": (214, 331),
"p5_educacion_ninguno": (285, 331),
"p5_educacion_tecnica_lab": (348, 331),
"p5_regimen_subsidiado": (171, 313),
"p5_regimen_contributivo": (246, 313),
"p5_regimen_especial": (326, 313),
"p5_regimen_excepcion": (394, 313),
"p5_regimen_no_afiliado": (465, 313),
"p5_prot_ninos": (53, 263),
"p5_prot_gestante": (188, 264),
"p5_prot_adulto_mayor": (256, 263),
"p5_prot_diversa": (372, 263),
"p5_prot_campesino": (53, 250),
"p5_prot_migrante": (176, 250),
"p5_prot_madre_cabeza": (247, 250),
"p5_prot_enf_huerfana": (370, 250),
"p5_prot_conflicto": (54, 235),
"p5_prot_violencia_genero": (192, 236),
"p5_prot_violencia_interpersonal": (392, 235),
"p5_prot_privada_libertad": (53, 221),
"p5_prot_penal_adolescente": (275, 221),
"p5_prot_otro": (53, 207),
"p5_prot_ninguna": (483, 207),
"p5_violencia_fisica": (472, 190),
"p5_violencia_psicologica": (54, 175),
"p5_violencia_negligencia": (130, 175),
"p5_violencia_sexual": (374, 175),
"p5_violencia_patrimonial": (434, 175),
"p5_etnia_indigena": (160, 158),
"p5_etnia_rrom": (226, 158),
"p5_etnia_negro": (314, 159),
"p5_etnia_afro": (372, 159),
"p5_etnia_raizal": (54, 145),
"p5_etnia_palenquero": (211, 144),
"p5_etnia_ninguna": (390, 144),


# -------------------------------------------------------------
# PÁGINA 6: SITUACIÓN DE SALUD, ACCESO A SERVICIOS Y CUIDADO
# -------------------------------------------------------------
"p6_anc_proteger": (64, 693),
"p6_anc_transicion": (64, 680),
"p6_anc_tradicionales": (64, 665),
"p6_anc_armonizacion": (64, 649),
"p6_anc_partera": (64, 634),
"p6_anc_cuidado_entorno": (64, 620),
"p6_anc_ninguna": (329, 620),
"p6_disc_fisica": (260, 603),
"p6_disc_auditiva": (315, 603),
"p6_disc_visual": (381, 603),
"p6_disc_sordoceguera": (439, 603),
"p6_disc_intelectual": (64, 589),
"p6_disc_psicosocial": (150, 589),
"p6_disc_multiple": (257, 589),
"p6_disc_ninguna": (322, 589),
"p6_cert_disc_si": (330, 571),
"p6_cert_disc_no": (426, 571),
"p6_cert_disc_no_aplica": (499, 572),
"p6_intencion_reproductiva_si": (225, 554),
"p6_intencion_reproductiva_no": (271, 554),
"p6_gestacion_si": (486, 554),
"p6_gestacion_no": (538, 554),
"p6_rut_alimentos": (64, 522),
"p6_rut_actividad": (339, 522),
"p6_rut_higiene": (64, 509),
"p6_rut_lavado": (64, 493),
"p6_rut_duerme": (64, 471),
"p6_rut_control": (64, 456),
"p6_rut_ocio": (64, 442),
"p6_rut_cultural": (64, 427),
"p6_rut_ninguna": (502, 427),
"p6_maint_pymes": (64, 395),
"p6_maint_bucal": (228, 395),
"p6_maint_lactancia": (64, 382),
"p6_maint_fluor": (242, 381),
"p6_maint_profilaxis": (344, 381),
"p6_maint_vacunas": (64, 367),
"p6_maint_fortificacion": (241, 367),
"p6_maint_suplementos": (64, 351),
"p6_maint_desparasitacion": (232, 353),
"p6_maint_anemia": (64, 338),
"p6_maint_asesoria": (323, 338),
"p6_maint_sum_anticonceptivos": (64, 323),
"p6_maint_cardiovascular": (410, 323),
"p6_maint_treponemica": (64, 309),
"p6_maint_vih": (197, 309),
"p6_maint_hepatitis": (64, 294),
"p6_maint_embarazo_prueba": (64, 279),
"p6_maint_cuello_uterino": (64, 265),
"p6_maint_colposcopia": (334, 265),
"p6_maint_mama": (64, 251),
"p6_maint_prostata": (210, 251),
"p6_maint_colon": (366, 251),
"p6_maint_educacion": (63, 237),
"p6_maint_ninguna": (196, 237),
"p6_mat_preconcepcional": (64, 205),
"p6_mat_ive": (340, 204),
"p6_mat_prenatal": (64, 191),
"p6_mat_preparacion": (340, 191),
"p6_mat_puerperio": (64, 176),
"p6_mat_metodo_post_parto": (202, 176),
"p6_mat_recien_nacido": (64, 161),
"p6_mat_educacion": (284, 161),
"p6_mat_ninguna": (426, 161),
"p6_mot_no_afiliado": (62, 127),
"p6_mot_desconocimiento_derecho": (136, 127),
"p6_mot_desconocimiento_gratuito": (352, 127),
"p6_mot_lejos": (63, 115),
"p6_mot_no_personal": (288, 113),
"p6_mot_tramites": (63, 99),
"p6_mot_no_agenda": (247, 99),
"p6_mot_no_sabe": (414, 99),
"p6_mot_horario": (63, 86),
"p6_mot_tiempos": (218, 85),
"p6_mot_no_comodo": (346, 85),
"p6_mot_enfermo": (63, 72),
"p6_mot_falta_tiempo": (274, 71),
"p6_mot_falta_adecuacion": (64, 57),
"p6_mot_ninguna": (262, 57),

"p7_peso": (170, 635),
"p7_talla": (170, 618),
"p7_circunferencia_cintura": (542, 635),
"p7_imc": (371, 618),
"p7_tension_sistolica": (156, 479),
"p7_tension_diastolica": (356, 479),

"p7_tension_no_aplica": (474, 479),

"p7_der_conoce": (64, 714),
"p7_der_info": (64, 701),
"p7_der_lugares": (64, 685),
"p7_der_resolver": (63, 671),
"p7_lactancia_si": (344, 652),
"p7_lactancia_no": (434, 652),
"p7_lactancia_no_aplica": (502, 652),
"p7_ant_obesidad": (63, 578),
"p7_ant_sobrepeso": (131, 578),
"p7_ant_riesgo_sobrepeso": (204, 578),
"p7_ant_peso_adecuado": (314, 578),
"p7_ant_riesgo_desnutricion": (64, 565),
"p7_ant_desnutricion_moderada": (396, 565),
"p7_ant_desnutricion_severa": (63, 543),
"p7_ant_riesgo_delgadez": (195, 543),
"p7_ant_delgadez": (301, 543),
"p7_ant_bajo_peso_gestacional": (368, 543),
"p7_ant_normal": (530, 543),
"p7_desn_cabeza": (416, 525),
"p7_desn_cara": (478, 525),
"p7_desn_piel": (529, 525),
"p7_desn_torax": (63, 511),
"p7_desn_extremidades": (162, 511),
"p7_desn_comportamiento": (246, 511),
"p7_desn_edema": (342, 511),
"p7_desn_ninguna": (404, 511),
"p7_desn_no_aplica": (469, 511),
"p7_ten_crisis": (64, 448),
"p7_ten_alta_2": (64, 435),
"p7_ten_alta_1": (64, 420),
"p7_ten_elevada": (63, 405),
"p7_ten_normal": (64, 389),
"p7_ent_obstetrica": (64, 358),
"p7_ent_cardiovascular": (63, 345),
"p7_ent_diabetes": (347, 345),
"p7_ent_cancer": (415, 345),
"p7_ten_no_aplica": (388, 390),
"p7_ent_epoc": (474, 345),
"p7_ent_raras": (63, 331),
"p7_ent_trastorno": (216, 330),
"p7_ent_epilepsia": (314, 330),
"p7_ent_secuelas": (63, 317),
"p7_ent_ninguna": (473, 316),
"p7_tra_infancia": (64, 285),
"p7_tra_tuberculosis": (469, 285),
"p7_tra_lepra": (63, 271),
"p7_tra_rabia": (121, 271),
"p7_tra_dengue": (176, 270),
"p7_tra_chikungunya": (239, 271),
"p7_tra_zika": (321, 271),
"p7_tra_chagas": (371, 271),
"p7_tra_visceral": (432, 271),
"p7_tra_cutanea": (64, 258),
"p7_tra_tungiasis": (182, 257),
"p7_tra_alimentos": (251, 257),
"p7_tra_era": (63, 243),
"p7_tra_eda": (234, 242),
"p7_tra_ninguna": (396, 242),
"p7_end_geohelmintiasis": (57, 211),
"p7_end_teniasis": (151, 211),
"p7_end_tracoma": (266, 211),
"p7_end_escabiosis": (332, 211),
"p7_end_pian": (404, 211),
"p7_end_malaria": (455, 211),
"p7_end_ninguna": (518, 211),
"p7_tratamiento_si": (404, 191),
"p7_tratamiento_no": (460, 191),
"p7_tratamiento_no_aplica": (519, 191),
"p7_mot_no_afiliado": (64, 154),
"p7_mot_lejos": (168, 155),
"p7_mot_tramites": (394, 155),
"p7_mot_no_agenda": (64, 141),
"p7_mot_no_sabe": (228, 141),
"p7_mot_no_pagar": (370, 141),
"p7_mot_horarios": (64, 127),
"p7_mot_tiempos": (219, 127),
"p7_mot_no_comodo": (349, 127),
"p7_mot_enfermo": (64, 113),
"p7_mot_no_adherencia": (275, 113),
"p7_mot_no_disponibilidad": (64, 98),
"p7_mot_falta_tiempo": (332, 98),
"p7_mot_falta_adecuacion": (64, 83),
"p7_mot_no_aplica": (280, 84),

"p7_tension_no_aplica": (474, 479),
"p7_tension_no_aplica": (474, 479),
"p8_puntaje_assist": (425, 512),
"p8_puntaje_audit": (217, 498),
"p8_puntaje_crafft": (487, 498),
"p8_riesgo_convivencia": (64, 706),
"p8_riesgo_nuevo_integrante": (214, 706),
"p8_riesgo_ingreso_estudiar": (362, 706),
"p8_riesgo_perdida_ano": (462, 706),
"p8_riesgo_embarazo": (64, 692),
"p8_riesgo_independencia": (222, 691),
"p8_riesgo_separacion": (439, 692),
"p8_riesgo_duelo": (538, 692),
"p8_riesgo_desempleo": (64, 678),
"p8_riesgo_crisis": (245, 677),
"p8_riesgo_conflictos": (382, 677),
"p8_riesgo_abandono": (63, 663),
"p8_riesgo_no_cuenta_redes": (196, 663),
"p8_riesgo_estigma": (464, 663),
"p8_riesgo_conflictos_orientacion": (63, 649),
"p8_riesgo_trastorno": (274, 649),
"p8_riesgo_ninguna": (522, 649),
"p8_triste_dos_semanas": (63, 616),
"p8_perdida_interes": (327, 616),
"p8_inquieto_nervioso": (63, 602),
"p8_salud_mental_ninguno": (413, 602),
"p8_salud_mental_no_aplica": (478, 603),
"p8_autolesion_si": (63, 571),
"p8_autolesion_ninguno": (380, 571),
"p8_autolesion_no_aplica": (506, 571),
"p8_consumo_si": (63, 531),
"p8_consumo_no": (350, 530),
"p8_consumo_no_aplica": (478, 530),
"p8_limita_si": (480, 482),
"p8_limita_no": (542, 482),


}

app = Flask(__name__)


def obtener_lista_segura(objeto_formulario, llave):
    """
    Obtiene una lista de valores de forma segura.
    Soporta tanto MultiDict de Flask (.getlist) como diccionarios estándar (.get).
    """
    if hasattr(objeto_formulario, 'getlist'):
        return objeto_formulario.getlist(llave)
    
    # Si es un diccionario plano
    valor = objeto_formulario.get(llave, [])
    if isinstance(valor, list):
        return valor
    return [valor] if valor else []

def generar_overlay_p1(datos, width, height):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    for campo in ["departamento", "uzpe", "municipio", "territorio", "microterritorio", "corregimiento_barrio", "id_equipo", "prestador_primario"]:
        if campo in COORD_P1:
            x, y = COORD_P1[campo]
            can.drawString(x, y, datos.get(campo, '').upper())

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
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    # 1. Procesar todos los Campos de Texto (Lista ampliada y corregida)
    campos_texto_p2 = [
        "p2_id_numero", "p2_perfil_profesional", "p2_codigo_ficha", "p2_fecha_ficha",
        "p2_direccion", "p2_latitud", "p2_longitud", "p2_punto_referencia", 
        "p2_id_hogar", "p2_id_familia", "p2_num_hogares", "p2_num_personas", 
        "p2_num_habitaciones", "p2_personas_habitacion", "p2_elementos_dormir",
        "p2_nombre_institucion", "p2_cabeza_familia" # <-- AGREGADOS CORRECTAMENTE
    ]
    for campo in campos_texto_p2:
        if campo in COORD_P2:
            x, y = COORD_P2[campo]
            can.drawString(x, y, datos.get(campo, '').upper())

    # 2. Procesar Radios
    tipo_id = datos.get('p2_id_tipo')
    key_tipo = f"p2_id_tipo_{str(tipo_id).lower()}"
    if key_tipo in COORD_P2: can.drawString(*COORD_P2[key_tipo], "X")

    entorno = datos.get('p2_entorno')
    key_entorno = f"p2_entorno_{str(entorno).lower()}"
    if key_entorno in COORD_P2: can.drawString(*COORD_P2[key_entorno], "X")

    j_paz = datos.get('p2_jovenes_paz')
    key_paz = f"p2_jovenes_paz_{str(j_paz).lower()}"
    if key_paz in COORD_P2: can.drawString(*COORD_P2[key_paz], "X")

    hacinamiento = datos.get('p2_hacinamiento')
    key_hac = f"p2_hacinamiento_{str(hacinamiento).lower()}"
    if key_hac in COORD_P2: can.drawString(*COORD_P2[key_hac], "X")

    t_vivienda = datos.get('p2_tipo_vivienda')
    key_viv = f"p2_tipo_vivienda_{str(t_vivienda).lower()}"
    if key_viv in COORD_P2: can.drawString(*COORD_P2[key_viv], "X")

    techo = datos.get('p2_techo')
    key_techo = f"p2_techo_{str(techo).lower()}"
    if key_techo in COORD_P2: can.drawString(*COORD_P2[key_techo], "X")

    # NUEVA LÓGICA DE PROCESAMIENTO DE ESTRATO (AGREGADA)
    estrato = datos.get('p2_estrato')
    if estrato:
        key_estrato = f"p2_estrato_{str(estrato).lower().replace('-', '_')}" # Asegura formato bajo_bajo
        if key_estrato in COORD_P2: can.drawString(*COORD_P2[key_estrato], "X")

    # 3. Procesar Riesgos (Checkboxes)
    for riesgo in riesgos:
        key_riesgo = f"p2_riesgo_{riesgo.lower()}"
        if key_riesgo in COORD_P2:
            can.drawString(*COORD_P2[key_riesgo], "X")

    can.save()
    packet.seek(0)
    return packet

def generar_overlay_p3(datos, riesgos, animales, width, height):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    # 1. Procesar Campos de Texto/Número
    campos_texto_p3 = [
        "p3_num_perros", "p3_num_perros_vacuna", 
        "p3_num_gatos", "p3_num_gatos_vacuna", 
        "p3_fam_personas"
    ]
    for campo in campos_texto_p3:
        if campo in COORD_P3:
            x, y = COORD_P3[campo]
            can.drawString(x, y, datos.get(campo, '').upper())

    # 2. Procesar Opciones Simples (Radios/Selects)
    # Criaderos (Radio)
    criaderos = datos.get('p3_criaderos')
    key_cria = f"p3_criaderos_{str(criaderos).lower()}"
    if key_cria in COORD_P3: can.drawString(*COORD_P3[key_cria], "X")

    # Actividad económica (Radio)
    act_eco = datos.get('p3_act_economica')
    key_eco = f"p3_act_economica_{str(act_eco).lower()}"
    if key_eco in COORD_P3: can.drawString(*COORD_P3[key_eco], "X")

    # Carnet de vacunación (Radio)
    carnet = datos.get('p3_carnet')
    key_car = f"p3_carnet_{str(carnet).lower()}"
    if key_car in COORD_P3: can.drawString(*COORD_P3[key_car], "X")

    # Fuentes de Agua (Select)
    agua = datos.get('p3_agua')
    key_agua = f"p3_agua_{str(agua).lower()}"
    if key_agua in COORD_P3: can.drawString(*COORD_P3[key_agua], "X")

    # Excretas (Select)
    excretas = datos.get('p3_exc')
    key_exc = f"p3_exc_{str(excretas).lower()}"
    if key_exc in COORD_P3: can.drawString(*COORD_P3[key_exc], "X")

    # Residuales (Select)
    res = datos.get('p3_res')
    key_res = f"p3_res_{str(res).lower()}"
    if key_res in COORD_P3: can.drawString(*COORD_P3[key_res], "X")

    # Sólidos (Select)
    sol = datos.get('p3_sol')
    key_sol = f"p3_sol_{str(sol).lower()}"
    if key_sol in COORD_P3: can.drawString(*COORD_P3[key_sol], "X")

    # Tipo Familia (Radio)
    t_fam = datos.get('p3_tipo_familia') # Ojo con el nombre del input en el HTML
    key_fam = f"p3_fam_{str(t_fam).lower()}"
    if key_fam in COORD_P3: can.drawString(*COORD_P3[key_fam], "X")

    # Cuidador principal (Radio)
    cuidador = datos.get('p3_cuidador')
    key_cui = f"p3_cuidador_{str(cuidador).lower()}"
    if key_cui in COORD_P3: can.drawString(*COORD_P3[key_cui], "X")

    # Zarit (Radio)
    zarit = datos.get('p3_zarit')
    key_zarit = f"p3_zarit_{str(zarit).lower()}"
    if key_zarit in COORD_P3: can.drawString(*COORD_P3[key_zarit], "X")

    # 3. Procesar Checkboxes Múltiples (Riesgos de entorno y Animales)
    for riesgo in riesgos:
        key_riesgo = f"p3_ent_{riesgo.lower()}"
        if key_riesgo in COORD_P3: can.drawString(*COORD_P3[key_riesgo], "X")

    for animal in animales:
        key_animal = f"p3_ani_{animal.lower()}"
        if key_animal in COORD_P3: can.drawString(*COORD_P3[key_animal], "X")

    can.save()
    packet.seek(0)
    return packet

def generar_overlay_p4(datos, riesgos, vinculos, hogar, width, height):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    # 1. Marcar Riesgos Familiares (Checkboxes)
    for riesgo in riesgos:
        key_riesgo = f"p4_riesgo_{riesgo.lower()}"
        if key_riesgo in COORD_P4:
            can.drawString(*COORD_P4[key_riesgo], "X")

    # 2. Marcar Vínculos Familiares (Checkboxes)
    for vinculo in vinculos:
        key_vinculo = f"p4_vinculo_{vinculo.lower()}"
        if key_vinculo in COORD_P4:
            can.drawString(*COORD_P4[key_vinculo], "X")

    # 3. Marcar Red de Apoyo (Radio)
    red_apoyo = datos.get('p4_red_apoyo')
    key_red = f"p4_red_{str(red_apoyo).lower()}"
    if key_red in COORD_P4:
        can.drawString(*COORD_P4[key_red], "X")

    # 4. Marcar Prácticas de Protección en el Hogar (Checkboxes)
    for practica in hogar:
        key_practica = f"p4_hogar_{practica.lower()}"
        if key_practica in COORD_P4:
            can.drawString(*COORD_P4[key_practica], "X")

    can.save()
    packet.seek(0)
    return packet

def generar_overlay_miembro(idx, form, width, height):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica-Bold", 9)

    # ---------------------------------------------
    # PÁGINA 5 (Familiar pág 1) - PROCESAMIENTO COMPLETO
    # ---------------------------------------------
    # 1. Campos de Texto / Números
    campos_texto_p5 = [
        "p5_primer_nombre", "p5_segundo_nombre", "p5_primer_apellido", "p5_segundo_apellido",
        "p5_id_numero", "p5_fecha_nacimiento", "p5_nacionalidad", "p5_telefono_1", "p5_telefono_2",
        "p5_ocupacion", "p5_eapb", "p5_pueblo_etnico",
        "p5_identidad_otro_cual", "p5_orientacion_otro_cual", "p5_prot_otro_cual"
    ]
    for campo in campos_texto_p5:
        field_name = f"m_{idx}_{campo}"
        if campo in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO[campo], form.get(field_name, '').upper())

    # 2. Selección Única (Desplegables / Radios)
    # Mapea el nombre del input en el HTML con el prefijo correspondiente en COORD_MIEMBRO
    radio_mappings_p5 = {
        "p5_id_tipo": "p5_id_tipo",
        "p5_sexo": "p5_sexo",
        "p5_genero": "p5_genero",
        "p5_identidad": "p5_identidad",
        "p5_orientacion": "p5_orientacion",
        "p5_rol": "p5_rol",
        "p5_educacion": "p5_educacion",
        "p5_regimen": "p5_regimen",
        "p5_violencia": "p5_violencia",
        "p5_etnia": "p5_etnia"
    }
    for key_html, coord_prefix in radio_mappings_p5.items():
        val = form.get(f"m_{idx}_{key_html}")
        if val:
            # Convierte valores como "Bajo-Bajo" o "Medio-Alto" para coincidir con la clave del diccionario
            val_limpio = str(val).lower().replace('-', '_')
            key_coord = f"{coord_prefix}_{val_limpio}"
            if key_coord in COORD_MIEMBRO:
                can.drawString(*COORD_MIEMBRO[key_coord], "X")

    # 3. Checkboxes de Especial Protección (Lista múltiple)
    protecciones = obtener_lista_segura(form, f"m_{idx}_p5_prot[]")
    for prot in protecciones:
        key_prot = f"p5_prot_{prot.lower()}"
        if key_prot in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO[key_prot], "X")

    # ---------------------------------------------
    # PÁGINA 6 (Familiar pág 2)
    # ---------------------------------------------
    can.showPage() 
    can.setFont("Helvetica-Bold", 9)

    # 1. Procesar Selección Única (Desplegables / Radios de Página 6)
    radio_mappings_p6 = {
        "p6_cert_disc": "p6_cert_disc",
        "p6_intencion_reproductiva": "p6_intencion_reproductiva",
        "p6_gestacion": "p6_gestacion"
    }
    for key_html, coord_prefix in radio_mappings_p6.items():
        val = form.get(f"m_{idx}_{key_html}")
        if val:
            key_coord = f"{coord_prefix}_{str(val).lower()}"
            if key_coord in COORD_MIEMBRO:
                can.drawString(*COORD_MIEMBRO[key_coord], "X")

    # 2. Procesar Checkboxes Grupales (Listas múltiples de Página 6)
    # Asocia el nombre del array del HTML con el prefijo en tu diccionario COORD_MIEMBRO
    checkbox_groups_p6 = {
        "p6_ancestrales[]": "p6_anc",
        "p6_discapacidad[]": "p6_disc",
        "p6_rutinarias[]": "p6_rut",
        "p6_maint[]": "p6_maint",
        "p6_materno[]": "p6_mat",
        "p6_motivos[]": "p6_mot"
    }
    
    for key_html, coord_prefix in checkbox_groups_p6.items():
        # Usamos el helper seguro para extraer la lista sin provocar errores de tipo 'dict'
        seleccionados = obtener_lista_segura(form, f"m_{idx}_{key_html}")
        for item in seleccionados:
            key_coord = f"{coord_prefix}_{str(item).lower()}"
            if key_coord in COORD_MIEMBRO:
                can.drawString(*COORD_MIEMBRO[key_coord], "X")


 
    # =============================================================
    # PÁGINA 7 (Familiar pág 3) - PROCESAMIENTO COMPLETO
    # =============================================================
    can.showPage() 
    can.setFont("Helvetica-Bold", 9)

    # 1. Procesar Campos de Texto / Números (Página 7)
    campos_texto_p7 = [
        "p7_peso", "p7_talla", "p7_circunferencia_cintura", 
        "p7_imc", "p7_tension_sistolica", "p7_tension_diastolica"
    ]
    for campo in campos_texto_p7:
        field_name = f"m_{idx}_{campo}"
        if campo in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO[campo], form.get(field_name, '').upper())

    # 2. Procesar Selección Única (Desplegables / Radios)
    radio_mappings_p7 = {
        "p7_lactancia": "p7_lactancia",
        "p7_antropometrico": "p7_ant",
        "p7_tension_clasificacion": "p7_ten",
        "p7_tratamiento": "p7_tratamiento"
    }
    for key_html, coord_prefix in radio_mappings_p7.items():
        val = form.get(f"m_{idx}_{key_html}")
        if val:
            key_coord = f"{coord_prefix}_{str(val).lower()}"
            if key_coord in COORD_MIEMBRO:
                can.drawString(*COORD_MIEMBRO[key_coord], "X")

    # Caso especial: Checkbox "No aplica" para tensión arterial
    if form.get(f"m_{idx}_p7_tension_no_aplica") == "Si":
        if "p7_ten_no_aplica" in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO["p7_tension_no_aplica"], "X")

    # 3. Procesar Checkboxes Grupales (Listas múltiples)
    checkbox_groups_p7 = {
        "p7_derechos[]": "p7_der",
        "p7_desnutricion_signos[]": "p7_desn",
        "p7_no_transmisibles[]": "p7_ent",
        "p7_transmisibles[]": "p7_tra",
        "p7_endemicas[]": "p7_end",
        "p7_no_atencion_motivos[]": "p7_mot"
    }
    for key_html, coord_prefix in checkbox_groups_p7.items():
        seleccionados = obtener_lista_segura(form, f"m_{idx}_{key_html}")
        for item in seleccionados:
            key_coord = f"{coord_prefix}_{str(item).lower()}"
            if key_coord in COORD_MIEMBRO:
                can.drawString(*COORD_MIEMBRO[key_coord], "X")

    # =============================================================
    # PÁGINA 8 (Familiar pág 4) - PROCESAMIENTO COMPLETO
    # =============================================================
    can.showPage() 
    can.setFont("Helvetica-Bold", 9)

    # 1. Procesar Campos de Texto / Números (Página 8)
    campos_texto_p8 = ["p8_puntaje_assist", "p8_puntaje_audit", "p8_puntaje_crafft"]
    for campo in campos_texto_p8:
        field_name = f"m_{idx}_{campo}"
        if campo in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO[campo], form.get(field_name, '').upper())

    # 2. Procesar Selección Única (Desplegables / Radios)
    radio_mappings_p8 = {
        "p8_autolesion": "p8_autolesion",
        "p8_consumo": "p8_consumo",
        "p8_limita": "p8_limita"
    }
    for key_html, coord_prefix in radio_mappings_p8.items():
        val = form.get(f"m_{idx}_{key_html}")
        if val:
            key_coord = f"{coord_prefix}_{str(val).lower()}"
            if key_coord in COORD_MIEMBRO:
                can.drawString(*COORD_MIEMBRO[key_coord], "X")

    # 3. Procesar Checkboxes (Riesgos Jóvenes de 14 a 28 años)
    riesgos_jovenes = obtener_lista_segura(form, f"m_{idx}_p8_jovenes_riesgos[]")
    for r in riesgos_jovenes:
        key_riesgo = f"p8_riesgo_{r.lower()}"
        if key_riesgo in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO[key_riesgo], "X")

    # 4. Procesar Checkboxes (Durante más de dos semanas)
    salud_mental = obtener_lista_segura(form, f"m_{idx}_p8_salud_mental[]")
    for sm in salud_mental:
        # Mapea los valores del formulario a sus respectivas claves en COORD_MIEMBRO
        mapping_sm = {
            "triste": "p8_triste_dos_semanas",
            "perder_interes": "p8_perdida_interes",
            "inquieto_nervioso": "p8_inquieto_nervioso",
            "ninguno": "p8_salud_mental_ninguno",
            "no_aplica": "p8_salud_mental_no_aplica"
        }
        key_sm = mapping_sm.get(sm.lower())
        if key_sm and key_sm in COORD_MIEMBRO:
            can.drawString(*COORD_MIEMBRO[key_sm], "X")

    # Fin del bloque del integrante
    can.save()
    packet.seek(0)
    return packet

@app.route('/')
def index():
    return render_template('formulario.html')


@app.route('/generar', methods=['POST'])
def generar():
    form_completo = request.form
    
    # Recogemos la lista de índices activos enviados por el HTML
    member_indices = obtener_lista_segura(form_completo, 'member_indices[]')

    # Separación lógica de datos de las pestañas fijas
    datos_p1 = {k: v for k, v in form_completo.items() if not k.startswith("p2_") and not k.startswith("p3_") and not k.startswith("p4_") and not k.startswith("m_")}
    datos_p2 = {k: v for k, v in form_completo.items() if k.startswith("p2_")}
    datos_p3 = {k: v for k, v in form_completo.items() if k.startswith("p3_")}
    datos_p4 = {k: v for k, v in form_completo.items() if k.startswith("p4_")}
    
    # Recoger listas de Checkboxes de páginas fijas
    riesgos_p2 = obtener_lista_segura(form_completo, 'p2_riesgos[]')
    riesgos_p3 = obtener_lista_segura(form_completo, 'p3_entorno_riesgos[]')
    animales_p3 = obtener_lista_segura(form_completo, 'p3_animales[]')
    riesgos_p4 = obtener_lista_segura(form_completo, 'p4_riesgos[]')
    vinculos_p4 = obtener_lista_segura(form_completo, 'p4_vinculos[]')
    hogar_p4 = obtener_lista_segura(form_completo, 'p4_hogar[]')

    try:
        reader = PdfReader("plantilla_ministerio.pdf")
        writer = PdfWriter()

        # =============================================================
        # FASE 1: PROCESAR Y AGREGAR PÁGINAS 1 A 4 (FIJAS)
        # =============================================================
        for idx in range(4):
            page = reader.pages[idx]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            
            x_offset = float(page.mediabox.left)
            y_offset = float(page.mediabox.bottom)
            
            overlay_packet = None
            desplazamiento_x = x_offset
            desplazamiento_y = y_offset

            if idx == 0:
                overlay_packet = generar_overlay_p1(datos_p1, width, height)
                desplazamiento_x += AJUSTE_MANUAL_X_P1
                desplazamiento_y += AJUSTE_MANUAL_Y_P1
            elif idx == 1:
                overlay_packet = generar_overlay_p2(datos_p2, riesgos_p2, width, height)
                desplazamiento_x += AJUSTE_MANUAL_X_P2
                desplazamiento_y += AJUSTE_MANUAL_Y_P2
            elif idx == 2:
                overlay_packet = generar_overlay_p3(datos_p3, riesgos_p3, animales_p3, width, height)
                desplazamiento_x += AJUSTE_MANUAL_X_P3
                desplazamiento_y += AJUSTE_MANUAL_Y_P3
            elif idx == 3:
                overlay_packet = generar_overlay_p4(datos_p4, riesgos_p4, vinculos_p4, hogar_p4, width, height)
                desplazamiento_x += AJUSTE_MANUAL_X_P4
                desplazamiento_y += AJUSTE_MANUAL_Y_P4

            # Fusión limpia (Se realiza una sola vez por página y con el ajuste correcto)
            if overlay_packet:
                overlay_reader = PdfReader(overlay_packet)
                overlay_page = overlay_reader.pages[0]
                if desplazamiento_x != 0 or desplazamiento_y != 0:
                    overlay_page.add_transformation(Transformation().translate(tx=desplazamiento_x, ty=desplazamiento_y))
                page.merge_page(overlay_page)
            
            writer.add_page(page)

        # =============================================================
        # FASE 2: PROCESAR INTEGRANTES DINÁMICAMENTE (REPETIR PÁGINAS 5 A 8)
        # =============================================================
        for m_idx in member_indices:
            # Re-leemos la plantilla para cada miembro para asegurar páginas limpias y evitar contaminación
            member_reader = PdfReader("plantilla_ministerio.pdf")
            
            ref_page = member_reader.pages[4] # Página 5 como referencia
            width = float(ref_page.mediabox.width)
            height = float(ref_page.mediabox.height)

            # Generar el overlay temporal de 4 páginas de este integrante
            overlay_packet = generar_overlay_miembro(m_idx, form_completo, width, height)
            overlay_reader = PdfReader(overlay_packet)

            # Mezclamos página por página del familiar (Páginas 5, 6, 7 y 8, índices 4, 5, 6, 7)
            for p_num in range(4):
                template_idx = 4 + p_num
                page = member_reader.pages[template_idx]
                
                # Leemos el desfase original de la página actual
                x_offset = float(page.mediabox.left)
                y_offset = float(page.mediabox.bottom)
                
                # Calculamos el ajuste manual correspondiente según la página del integrante
                desplazamiento_x = x_offset
                desplazamiento_y = y_offset
                
                if p_num == 0:  # Página 5
                    desplazamiento_x += AJUSTE_MANUAL_X_P5 if 'AJUSTE_MANUAL_X_P5' in globals() else 0
                    desplazamiento_y += AJUSTE_MANUAL_Y_P5 if 'AJUSTE_MANUAL_Y_P5' in globals() else 0
                elif p_num == 1:  # Página 6
                    desplazamiento_x += AJUSTE_MANUAL_X_P6 if 'AJUSTE_MANUAL_X_P6' in globals() else 0
                    desplazamiento_y += AJUSTE_MANUAL_Y_P6 if 'AJUSTE_MANUAL_Y_P6' in globals() else 0
                elif p_num == 2:  # Página 7
                    desplazamiento_x += AJUSTE_MANUAL_X_P7 if 'AJUSTE_MANUAL_X_P7' in globals() else 0
                    desplazamiento_y += AJUSTE_MANUAL_Y_P7 if 'AJUSTE_MANUAL_Y_P7' in globals() else 0
                elif p_num == 3:  # Página 8
                    desplazamiento_x += AJUSTE_MANUAL_X_P8 if 'AJUSTE_MANUAL_X_P8' in globals() else 0
                    desplazamiento_y += AJUSTE_MANUAL_Y_P8 if 'AJUSTE_MANUAL_Y_P8' in globals() else 0

                # Aplicamos la transformación milimétrica
                overlay_page = overlay_reader.pages[p_num]
                if desplazamiento_x != 0 or desplazamiento_y != 0:
                    overlay_page.add_transformation(Transformation().translate(tx=desplazamiento_x, ty=desplazamiento_y))
                
                page.merge_page(overlay_page)
                writer.add_page(page)

        # =============================================================
        # FASE 3: COPIAR PÁGINAS FINALES 9 A 11 (CUIDADO DE VIVIENDA / FAMILIA)
        # =============================================================
        for idx in range(8, len(reader.pages)):
            writer.add_page(reader.pages[idx])

        # Generación del archivo en memoria y descarga
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name="APS_Ficha_Completa.pdf")
        
    except Exception as e:
        return f"Error al procesar el PDF: {e}"

if __name__ == '__main__':
    app.run(debug=True)