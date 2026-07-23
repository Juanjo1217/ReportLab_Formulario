import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:open_file_plus/open_file_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:share_plus/share_plus.dart';
import '../models/pdf_record.dart';
import '../services/pdf_stamper_service.dart';

class FormWebviewScreen extends StatefulWidget {
  final VoidCallback? onNavigateToHistory;

  const FormWebviewScreen({super.key, this.onNavigateToHistory});

  @override
  State<FormWebviewScreen> createState() => _FormWebviewScreenState();
}

class _FormWebviewScreenState extends State<FormWebviewScreen> {
  InAppWebViewController? _webViewController;
  bool _isProcessing = false;
  double _loadProgress = 0;

  @override
  void initState() {
    super.initState();
    _requestStoragePermissions();
  }

  Future<void> _requestStoragePermissions() async {
    if (await Permission.storage.isDenied) {
      await Permission.storage.request();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Diligenciar Formulario APS'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _webViewController?.reload(),
            tooltip: 'Recargar Formulario',
          ),
        ],
      ),
      body: Stack(
        children: [
          InAppWebView(
            initialFile: 'assets/html/formulario.html',
            initialSettings: InAppWebViewSettings(
              javaScriptEnabled: true,
              domStorageEnabled: true,
              useShouldOverrideUrlLoading: true,
              allowFileAccessFromFileURLs: true,
              allowUniversalAccessFromFileURLs: true,
            ),
            onWebViewCreated: (controller) {
              _webViewController = controller;

              // Inyectar polyfill para hacer compatible window.pywebview con Flutter InAppWebView
              controller.addJavaScriptHandler(
                handlerName: 'generar_pdf',
                callback: (args) async {
                  if (args.isNotEmpty) {
                    final rawData = args[0];
                    Map<String, dynamic> formData = {};
                    if (rawData is Map) {
                      formData = Map<String, dynamic>.from(rawData);
                    } else if (rawData is String) {
                      formData = json.decode(rawData);
                    }

                    await _processFormAndGeneratePdf(formData);
                    return {'success': true};
                  }
                  return {'success': false, 'error': 'Sin datos'};
                },
              );
            },
            onLoadStop: (controller, url) async {
              // Inyectar script de compatibilidad pywebview -> Flutter
              await controller.evaluateJavascript(source: '''
                window.pywebview = {
                  api: {
                    generar_pdf: function(data) {
                      return window.flutter_inappwebview.callHandler('generar_pdf', data);
                    }
                  }
                };
              ''');
            },
            onProgressChanged: (controller, progress) {
              setState(() {
                _loadProgress = progress / 100;
              });
            },
          ),
          if (_loadProgress < 1.0)
            LinearProgressIndicator(value: _loadProgress, color: Colors.teal),
          if (_isProcessing)
            Container(
              color: Colors.black54,
              child: const Center(
                child: Card(
                  margin: EdgeInsets.all(24),
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(color: Colors.teal),
                        SizedBox(height: 16),
                        Text(
                          'Generando y estampando PDF...',
                          style: TextStyle(
                              fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 8),
                        Text(
                          'Insertando coordenadas y organizando integrantes...',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _processFormAndGeneratePdf(Map<String, dynamic> formData) async {
    setState(() => _isProcessing = true);
    try {
      final PdfRecord record = await PdfStamperService.generateAndSavePdf(formData);
      setState(() => _isProcessing = false);

      if (mounted) {
        _showSuccessDialog(record);
      }
    } catch (e) {
      setState(() => _isProcessing = false);
      if (mounted) {
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Error al generar PDF'),
            content: Text('Ocurrió un error inesperado:\n$e'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Aceptar'),
              ),
            ],
          ),
        );
      }
    }
  }

  void _showSuccessDialog(PdfRecord record) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.teal.shade50,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check_circle, color: Colors.teal, size: 64),
            ),
            const SizedBox(height: 16),
            const Text(
              '¡PDF Generado con Éxito!',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Guardado en Descargas:\n${record.filename}',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade700, fontSize: 13),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  OpenFile.open(record.filePath);
                },
                icon: const Icon(Icons.picture_as_pdf, color: Colors.white),
                label: const Text('ABRIR PDF AHORA',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      Share.shareXFiles([XFile(record.filePath)]);
                    },
                    icon: const Icon(Icons.share),
                    label: const Text('Compartir'),
                    style: OutlinedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      if (widget.onNavigateToHistory != null) {
                        widget.onNavigateToHistory!();
                      }
                    },
                    icon: const Icon(Icons.folder_outlined),
                    label: const Text('Ver en Mis PDFs'),
                    style: OutlinedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
