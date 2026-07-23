import 'package:flutter/material.dart';
import 'package:open_file_plus/open_file_plus.dart';
import 'package:share_plus/share_plus.dart';
import '../models/pdf_record.dart';
import '../services/pdf_history_service.dart';

class PdfManagerScreen extends StatefulWidget {
  const PdfManagerScreen({super.key});

  @override
  State<PdfManagerScreen> createState() => _PdfManagerScreenState();
}

class _PdfManagerScreenState extends State<PdfManagerScreen> {
  List<PdfRecord> _allRecords = [];
  List<PdfRecord> _filteredRecords = [];
  bool _isLoading = true;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    final records = await PdfHistoryService.getRecords();
    setState(() {
      _allRecords = records;
      _filteredRecords = records;
      _isLoading = false;
    });
  }

  void _filterRecords(String query) {
    if (query.trim().isEmpty) {
      setState(() => _filteredRecords = _allRecords);
    } else {
      final q = query.toLowerCase();
      setState(() {
        _filteredRecords = _allRecords.where((r) {
          return r.filename.toLowerCase().contains(q) ||
              r.familyHeadName.toLowerCase().contains(q) ||
              r.formattedDate.contains(q);
        }).toList();
      });
    }
  }

  Future<void> _openPdf(PdfRecord record) async {
    final result = await OpenFile.open(record.filePath);
    if (result.type != ResultType.done && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('No se pudo abrir el archivo: ${result.message}'),
          backgroundColor: Colors.redAccent,
        ),
      );
    }
  }

  Future<void> _sharePdf(PdfRecord record) async {
    await Share.shareXFiles(
      [XFile(record.filePath)],
      text: 'Adjunto Formulario APS PDF - ${record.familyHeadName}',
    );
  }

  Future<void> _deletePdf(PdfRecord record) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('¿Eliminar PDF?'),
        content: Text(
            '¿Estás seguro de que deseas eliminar permanentemente el archivo "${record.filename}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Eliminar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await PdfHistoryService.deleteRecord(record.id);
      _loadHistory();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Archivo eliminado correctamente.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis PDFs Generados'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHistory,
            tooltip: 'Actualizar lista',
          ),
        ],
      ),
      body: Column(
        children: [
          // Barra de búsqueda
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              controller: _searchController,
              onChanged: _filterRecords,
              decoration: InputDecoration(
                hintText: 'Buscar por nombre, cabeza de hogar o fecha...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _filterRecords('');
                        },
                      )
                    : null,
                filled: true,
                fillColor: Colors.grey.shade100,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredRecords.isEmpty
                    ? _buildEmptyState()
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        itemCount: _filteredRecords.length,
                        itemBuilder: (ctx, idx) {
                          final record = _filteredRecords[idx];
                          return _buildPdfCard(record);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.picture_as_pdf_outlined,
                size: 80, color: Colors.teal.shade200),
            const SizedBox(height: 16),
            const Text(
              'No hay archivos PDF guardados',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Los formularios que diligencies y generes aparecerán organizados en esta pantalla.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPdfCard(PdfRecord record) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.picture_as_pdf, color: Colors.red),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        record.familyHeadName.isNotEmpty
                            ? record.familyHeadName
                            : record.filename,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 16),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${record.formattedDate} • ${record.formattedSize}',
                        style: TextStyle(
                            color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (val) {
                    if (val == 'delete') _deletePdf(record);
                  },
                  itemBuilder: (ctx) => [
                    const PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete, color: Colors.redAccent, size: 20),
                          SizedBox(width: 8),
                          Text('Eliminar', style: TextStyle(color: Colors.redAccent)),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const Divider(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: () => _sharePdf(record),
                  icon: const Icon(Icons.share, size: 18),
                  label: const Text('Compartir'),
                  style: OutlinedButton.styleFrom(
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () => _openPdf(record),
                  icon: const Icon(Icons.visibility, size: 18, color: Colors.white),
                  label: const Text('Abrir PDF', style: TextStyle(color: Colors.white)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
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
