import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class FitmentSelection {
  final String? makeId;
  final String? makeSlug;
  final String? makeName;
  final String? modelId;
  final String? modelSlug;
  final String? modelName;
  final int? year;
  final String? carYearId;

  const FitmentSelection({
    this.makeId,
    this.makeSlug,
    this.makeName,
    this.modelId,
    this.modelSlug,
    this.modelName,
    this.year,
    this.carYearId,
  });

  bool get isComplete =>
      carYearId != null && makeName != null && modelName != null && year != null;

  String get label {
    if (!isComplete) return 'اختر سيارتك';
    return '$year $makeName $modelName';
  }

  Map<String, dynamic> toJson() => {
        'make_id': makeId,
        'make_slug': makeSlug,
        'make_name': makeName,
        'model_id': modelId,
        'model_slug': modelSlug,
        'model_name': modelName,
        'year': year,
        'car_year_id': carYearId,
      };

  factory FitmentSelection.fromJson(Map<String, dynamic> json) {
    return FitmentSelection(
      makeId: json['make_id'] as String?,
      makeSlug: json['make_slug'] as String?,
      makeName: json['make_name'] as String?,
      modelId: json['model_id'] as String?,
      modelSlug: json['model_slug'] as String?,
      modelName: json['model_name'] as String?,
      year: json['year'] as int?,
      carYearId: json['car_year_id'] as String?,
    );
  }
}

class FitmentStorage {
  FitmentStorage._();
  static final FitmentStorage instance = FitmentStorage._();
  static const _key = 'rousto_fitment_selection';

  FitmentSelection? _cached;

  FitmentSelection? get current => _cached;

  Future<FitmentSelection?> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null) return null;
    try {
      _cached = FitmentSelection.fromJson(
        jsonDecode(raw) as Map<String, dynamic>,
      );
      return _cached;
    } catch (_) {
      return null;
    }
  }

  Future<void> save(FitmentSelection selection) async {
    _cached = selection;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(selection.toJson()));
  }

  Future<void> clear() async {
    _cached = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
