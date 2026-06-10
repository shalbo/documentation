import 'package:flutter/material.dart';

import '../features/fitment/data/repositories/fitment_repository.dart';
import '../services/fitment_storage.dart';
import '../theme/app_colors.dart';

class VehicleSelector extends StatefulWidget {
  final ValueChanged<FitmentSelection?> onChanged;

  const VehicleSelector({super.key, required this.onChanged});

  @override
  State<VehicleSelector> createState() => _VehicleSelectorState();
}

class _VehicleSelectorState extends State<VehicleSelector> {
  final _fitment = FitmentRepository();

  List<Map<String, dynamic>> _makes = [];
  List<Map<String, dynamic>> _models = [];
  List<Map<String, dynamic>> _years = [];

  String? _makeId;
  String? _modelId;
  String? _carYearId;
  int? _year;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    final saved = await FitmentStorage.instance.load();
    await _loadMakes();
    if (saved?.makeId != null) {
      _makeId = saved!.makeId;
      await _loadModels(_makeId!);
      if (saved.modelId != null) {
        _modelId = saved.modelId;
        await _loadYears(_modelId!);
        _carYearId = saved.carYearId;
        _year = saved.year;
      }
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _loadMakes() async {
    try {
      final res = await _fitment.getMakes();
      _makes = res;
    } catch (_) {}
  }

  Future<void> _loadModels(String makeId) async {
    try {
      _models = await _fitment.getModels(makeId);
    } catch (_) {
      _models = [];
    }
  }

  Future<void> _loadYears(String modelId) async {
    try {
      _years = await _fitment.getYears(modelId);
    } catch (_) {
      _years = [];
    }
  }

  Future<void> _persist() async {
    if (_makeId == null || _modelId == null || _carYearId == null || _year == null) {
      await FitmentStorage.instance.clear();
      widget.onChanged(null);
      return;
    }
    final make = _makes.firstWhere((m) => m['id'] == _makeId);
    final model = _models.firstWhere((m) => m['id'] == _modelId);
    final selection = FitmentSelection(
      makeId: _makeId,
      makeSlug: make['slug'] as String?,
      makeName: (make['name_ar'] ?? make['name']) as String?,
      modelId: _modelId,
      modelSlug: model['slug'] as String?,
      modelName: (model['name_ar'] ?? model['name']) as String?,
      year: _year,
      carYearId: _carYearId,
    );
    await FitmentStorage.instance.save(selection);
    widget.onChanged(selection);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const SizedBox(
        height: 44,
        child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
      );
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.directions_car_filled_outlined,
                  color: Colors.white, size: 18),
              SizedBox(width: 6),
              Text('محدد السيارة — Exact Fit',
                  style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                      fontSize: 12)),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(child: _dropdown(
                hint: 'الماركة',
                value: _makeId,
                items: _makes
                    .map((m) => DropdownMenuItem(
                          value: m['id'] as String,
                          child: Text(
                            (m['name_ar'] ?? m['name']).toString(),
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 13),
                          ),
                        ))
                    .toList(),
                onChanged: (v) async {
                  setState(() {
                    _makeId = v;
                    _modelId = null;
                    _carYearId = null;
                    _year = null;
                    _models = [];
                    _years = [];
                  });
                  if (v != null) await _loadModels(v);
                  setState(() {});
                  await _persist();
                },
              )),
              const SizedBox(width: 8),
              Expanded(
                child: _dropdown(
                  hint: 'الموديل',
                  value: _modelId,
                  items: _models
                      .map((m) => DropdownMenuItem(
                            value: m['id'] as String,
                            child: Text(
                              (m['name_ar'] ?? m['name']).toString(),
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontSize: 13),
                            ),
                          ))
                      .toList(),
                  onChanged: _makeId == null
                      ? null
                      : (v) async {
                          setState(() {
                            _modelId = v;
                            _carYearId = null;
                            _year = null;
                            _years = [];
                          });
                          if (v != null) await _loadYears(v);
                          setState(() {});
                          await _persist();
                        },
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _dropdown(
                  hint: 'السنة',
                  value: _carYearId,
                  items: _years
                      .map((y) => DropdownMenuItem(
                            value: y['id'] as String,
                            child: Text('${y['year']}',
                                style: const TextStyle(fontSize: 13)),
                          ))
                      .toList(),
                  onChanged: _modelId == null
                      ? null
                      : (v) async {
                          final row =
                              _years.firstWhere((y) => y['id'] == v);
                          setState(() {
                            _carYearId = v;
                            _year = row['year'] as int?;
                          });
                          await _persist();
                        },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _dropdown({
    required String hint,
    required String? value,
    required List<DropdownMenuItem<String>> items,
    required ValueChanged<String?>? onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(10),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          isExpanded: true,
          hint: Text(hint, style: const TextStyle(fontSize: 12)),
          value: items.any((i) => i.value == value) ? value : null,
          items: items,
          onChanged: onChanged,
        ),
      ),
    );
  }
}
