import 'dart:convert';
import 'dart:io';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/pdf_record.dart';

class PdfHistoryService {
  static const String _keyHistory = 'pdf_history_records';

  static Future<List<PdfRecord>> getRecords() async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> rawList = prefs.getStringList(_keyHistory) ?? [];
    List<PdfRecord> records = [];

    for (var raw in rawList) {
      try {
        final record = PdfRecord.fromJson(raw);
        // Verify if file still exists on disk
        if (File(record.filePath).existsSync()) {
          records.add(record);
        }
      } catch (_) {}
    }

    // Sort newest first
    records.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return records;
  }

  static Future<void> saveRecord(PdfRecord record) async {
    final prefs = await SharedPreferences.getInstance();
    final records = await getRecords();
    records.insert(0, record);

    final List<String> rawList =
        records.map((r) => json.encode(r.toMap())).toList();
    await prefs.setStringList(_keyHistory, rawList);
  }

  static Future<void> deleteRecord(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final records = await getRecords();

    // Delete file if exists
    final target = records.firstWhere(
      (r) => r.id == id,
      orElse: () => PdfRecord(
        id: '',
        filename: '',
        filePath: '',
        familyHeadName: '',
        createdAt: DateTime.now(),
        fileSizeBytes: 0,
      ),
    );

    if (target.filePath.isNotEmpty) {
      final file = File(target.filePath);
      if (file.existsSync()) {
        try {
          await file.delete();
        } catch (_) {}
      }
    }

    records.removeWhere((r) => r.id == id);
    final List<String> rawList =
        records.map((r) => json.encode(r.toMap())).toList();
    await prefs.setStringList(_keyHistory, rawList);
  }
}
