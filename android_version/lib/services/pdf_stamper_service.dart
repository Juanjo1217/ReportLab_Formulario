import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:syncfusion_flutter_pdf/pdf.dart';
import '../models/pdf_record.dart';
import 'pdf_history_service.dart';

class PdfStamperService {
  static Future<PdfRecord> generateAndSavePdf(Map<String, dynamic> formData) async {
    // 1. Cargar coordenadas y variables de ajuste
    final String coordsJson = await rootBundle.loadString('assets/json/coords.json');
    final Map<String, dynamic> config = json.decode(coordsJson);

    // 2. Cargar plantilla PDF
    final ByteData templateBytes = await rootBundle.load('assets/pdf/plantilla_ministerio.pdf');
    final List<int> bytes = templateBytes.buffer.asUint8List();
    final PdfDocument srcDoc = PdfDocument(inputBytes: bytes);

    // Identificar cantidad de miembros en el formulario
    int memberCount = 0;
    while (formData.containsKey('m_${memberCount}_p5_primer_nombre') ||
           formData.containsKey('m_${memberCount}_p5_id_numero') ||
           formData.containsKey('m_${memberCount}_p5_primer_apellido')) {
      memberCount++;
    }
    if (memberCount == 0) memberCount = 1; // Mínimo 1 integrante

    // Identificar cantidad de secciones P11 (Planes de cuidado)
    int p11Count = 0;
    while (formData.containsKey('p11_idx_${p11Count}_p11_situacion') ||
           formData.containsKey('p11_idx_${p11Count}_p11_compromiso')) {
      p11Count++;
    }
    if (p11Count == 0) p11Count = 1;

    // 3. Crear documento destino clonando páginas según la cantidad de integrantes
    final PdfDocument outDoc = PdfDocument();
    
    // Página 1 a 4 (Índices 0, 1, 2, 3)
    for (int i = 0; i < 4; i++) {
      outDoc.pages.add().graphics.drawPdfTemplate(
        srcDoc.pages[i].createTemplate(),
        const Offset(0, 0),
      );
    }

    // Páginas 5 a 8 por cada integrante
    for (int m = 0; m < memberCount; m++) {
      for (int p = 4; p <= 7; p++) {
        outDoc.pages.add().graphics.drawPdfTemplate(
          srcDoc.pages[p].createTemplate(),
          const Offset(0, 0),
        );
      }
    }

    // Página 9 (Índice plantilla 8)
    outDoc.pages.add().graphics.drawPdfTemplate(
      srcDoc.pages[8].createTemplate(),
      const Offset(0, 0),
    );

    // Página 10 (Índice plantilla 9)
    outDoc.pages.add().graphics.drawPdfTemplate(
      srcDoc.pages[9].createTemplate(),
      const Offset(0, 0),
    );

    // Página 11 (Índice plantilla 10) x p11Count
    for (int k = 0; k < p11Count; k++) {
      outDoc.pages.add().graphics.drawPdfTemplate(
        srcDoc.pages[10].createTemplate(),
        const Offset(0, 0),
      );
    }

    // 4. Estampar datos por página
    final font = PdfStandardFont(PdfFontFamily.helvetica, 9, style: PdfFontStyle.bold);

    // P1
    _stampPage(outDoc.pages[0], config['COORD_P1'] ?? {}, config, 'P1', formData, '', font);

    // P2
    _stampPage(outDoc.pages[1], config['COORD_P2'] ?? {}, config, 'P2', formData, '', font);

    // P3
    _stampPage(outDoc.pages[2], config['COORD_P3'] ?? {}, config, 'P3', formData, '', font);

    // P4
    _stampPage(outDoc.pages[3], config['COORD_P4'] ?? {}, config, 'P4', formData, '', font);

    // Integrantes (P5-P8)
    for (int m = 0; m < memberCount; m++) {
      final prefix = 'm_${m}_';
      final p5PageIdx = 4 + (4 * m);
      final p6PageIdx = 4 + (4 * m) + 1;
      final p7PageIdx = 4 + (4 * m) + 2;
      final p8PageIdx = 4 + (4 * m) + 3;

      _stampPage(outDoc.pages[p5PageIdx], config['COORD_MIEMBRO'] ?? {}, config, 'P5', formData, prefix, font);
      _stampPage(outDoc.pages[p6PageIdx], config['COORD_MIEMBRO'] ?? {}, config, 'P6', formData, prefix, font);
      _stampPage(outDoc.pages[p7PageIdx], config['COORD_MIEMBRO'] ?? {}, config, 'P7', formData, prefix, font);
      _stampPage(outDoc.pages[p8PageIdx], config['COORD_MIEMBRO'] ?? {}, config, 'P8', formData, prefix, font);
    }

    // P9
    final p9Idx = 4 + (4 * memberCount);
    _stampPage(outDoc.pages[p9Idx], config['COORD_P9'] ?? {}, config, 'P9', formData, '', font);

    // P10
    final p10Idx = 4 + (4 * memberCount) + 1;
    _stampPage(outDoc.pages[p10Idx], config['COORD_P10'] ?? {}, config, 'P10', formData, '', font);

    // P11
    for (int k = 0; k < p11Count; k++) {
      final p11Idx = 4 + (4 * memberCount) + 2 + k;
      final prefix = 'p11_idx_${k}_';
      _stampPage(outDoc.pages[p11Idx], config['COORD_P11'] ?? {}, config, 'P11', formData, prefix, font);
    }

    // 5. Guardar archivo en disco
    final String headName = _extractFamilyHeadName(formData);
    final String fileName = _buildFileName(headName);

    final Directory? downloadsDir = await _getExportDirectory();
    final String targetPath = '${downloadsDir!.path}/$fileName';

    final List<int> outBytes = await outDoc.save();
    outDoc.dispose();
    srcDoc.dispose();

    final File savedFile = File(targetPath);
    await savedFile.writeAsBytes(outBytes, flush: true);

    // 6. Registrar en historial
    final record = PdfRecord(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      filename: fileName,
      filePath: targetPath,
      familyHeadName: headName,
      createdAt: DateTime.now(),
      fileSizeBytes: outBytes.length,
    );

    await PdfHistoryService.saveRecord(record);
    return record;
  }

  static void _stampPage(
    PdfPage page,
    Map<String, dynamic> coordMap,
    Map<String, dynamic> config,
    String pageTag,
    Map<String, dynamic> formData,
    String prefix,
    PdfFont font,
  ) {
    final double pageHeight = page.size.height;

    final double adjX = (config['AJUSTE_MANUAL_X_$pageTag'] ?? 0).toDouble();
    final double adjY = (config['AJUSTE_MANUAL_Y_$pageTag'] ?? 0).toDouble();

    // Procesar mapeo de coordenadas
    coordMap.forEach((fieldKey, coordVal) {
      if (coordVal is List && coordVal.length == 2) {
        final double rlX = (coordVal[0] as num).toDouble();
        final double rlY = (coordVal[1] as num).toDouble();

        // Conversión ReportLab -> Syncfusion PDF
        final double flutterX = rlX + adjX;
        final double flutterY = pageHeight - rlY - adjY - 9.0;

        // Verificar si el campo o la marca existe en formData
        final String lookupKey = prefix.isNotEmpty ? '$prefix$fieldKey' : fieldKey;

        if (formData.containsKey(lookupKey)) {
          final dynamic rawVal = formData[lookupKey];
          final String textToDraw = _resolveTextToDraw(fieldKey, rawVal);
          if (textToDraw.isNotEmpty) {
            page.graphics.drawString(
              textToDraw,
              font,
              bounds: Rect.fromLTWH(flutterX, flutterY, 300, 20),
            );
          }
        } else {
          // Evaluar casos especiales o banderas 'X' de radios/checkboxes
          final String valueToDraw = _checkSpecialField(fieldKey, lookupKey, formData);
          if (valueToDraw.isNotEmpty) {
            page.graphics.drawString(
              valueToDraw,
              font,
              bounds: Rect.fromLTWH(flutterX, flutterY, 300, 20),
            );
          }
        }
      }
    });
  }

  static String _resolveTextToDraw(String fieldKey, dynamic rawVal) {
    if (rawVal == null) return '';
    if (rawVal is bool) return rawVal ? 'X' : '';
    if (rawVal is List) {
      return rawVal.join(', ').toUpperCase();
    }
    final str = rawVal.toString().trim();
    if (str.toUpperCase() == 'SI' || str.toUpperCase() == 'NO' || str == '1' || str == 'true') {
      return str.toUpperCase() == 'NO' ? 'NO' : 'X';
    }
    return str.toUpperCase();
  }

  static String _checkSpecialField(String fieldKey, String lookupKey, Map<String, dynamic> formData) {
    // Si el nombre exacto con prefijo coincide con un valor activo
    for (var entry in formData.entries) {
      final key = entry.key;
      final val = entry.value;

      if (key.endsWith('[]') && val is List) {
        for (var item in val) {
          if (fieldKey.contains(item.toString().toLowerCase())) {
            return 'X';
          }
        }
      } else if (val != null) {
        final valStr = val.toString().toLowerCase();
        if (fieldKey.endsWith('_$valStr') || fieldKey == valStr) {
          return 'X';
        }
      }
    }
    return '';
  }

  static String _extractFamilyHeadName(Map<String, dynamic> formData) {
    final String p1Head = formData['p2_cabeza_familia']?.toString() ?? '';
    if (p1Head.trim().isNotEmpty) return p1Head.trim();

    final String m0Nombre = '${formData['m_0_p5_primer_nombre'] ?? ''} ${formData['m_0_p5_primer_apellido'] ?? ''}'.trim();
    if (m0Nombre.isNotEmpty) return m0Nombre;

    return 'Ficha_APS';
  }

  static String _buildFileName(String headName) {
    final cleanName = headName.replaceAll(RegExp(r'[^\w\s\-]'), '').replaceAll(RegExp(r'\s+'), '_');
    final String timestamp = DateTime.now().millisecondsSinceEpoch.toString().substring(7);
    return 'Ficha_APS_${cleanName}_$timestamp.pdf';
  }

  static Future<Directory?> _getExportDirectory() async {
    if (Platform.isAndroid) {
      final Directory downloads = Directory('/storage/emulated/0/Download');
      if (downloads.existsSync()) {
        return downloads;
      }
    }
    return await getApplicationDocumentsDirectory();
  }
}
