import 'dart:convert';

class PdfRecord {
  final String id;
  final String filename;
  final String filePath;
  final String familyHeadName;
  final DateTime createdAt;
  final int fileSizeBytes;

  PdfRecord({
    required this.id,
    required this.filename,
    required this.filePath,
    required this.familyHeadName,
    required this.createdAt,
    required this.fileSizeBytes,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'filename': filename,
      'filePath': filePath,
      'familyHeadName': familyHeadName,
      'createdAt': createdAt.toIso8601String(),
      'fileSizeBytes': fileSizeBytes,
    };
  }

  factory PdfRecord.fromMap(Map<String, dynamic> map) {
    return PdfRecord(
      id: map['id'] ?? '',
      filename: map['filename'] ?? '',
      filePath: map['filePath'] ?? '',
      familyHeadName: map['familyHeadName'] ?? 'Ficha APS',
      createdAt: DateTime.tryParse(map['createdAt'] ?? '') ?? DateTime.now(),
      fileSizeBytes: map['fileSizeBytes'] ?? 0,
    );
  }

  String toJson() => json.encode(toMap());

  factory PdfRecord.fromJson(String source) =>
      PdfRecord.fromMap(json.decode(source));

  String get formattedSize {
    if (fileSizeBytes < 1024) return '$fileSizeBytes B';
    if (fileSizeBytes < 1024 * 1024) {
      return '${(fileSizeBytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(fileSizeBytes / (1024 * 1024)).toStringAsFixed(2)} MB';
  }

  String get formattedDate {
    final day = createdAt.day.toString().padLeft(2, '0');
    final month = createdAt.month.toString().padLeft(2, '0');
    final year = createdAt.year;
    final hour = createdAt.hour.toString().padLeft(2, '0');
    final minute = createdAt.minute.toString().padLeft(2, '0');
    return '$day/$month/$year $hour:$minute';
  }
}
