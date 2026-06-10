import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../data/app_repository.dart';
import '../data/models.dart';
import '../theme/app_colors.dart';
import '../theme/app_decorations.dart';
import '../currency.dart';

enum _SearchMode { name, oem, vin }

class PartsScreen extends StatefulWidget {
  final String? initialQuery;
  final String? initialCategory;
  final String? initialCarYearId;
  final String? initialCategoryId;
  final String? categoryLabel;
  final bool openVinMode;

  const PartsScreen({
    super.key,
    this.initialQuery,
    this.initialCategory,
    this.initialCarYearId,
    this.initialCategoryId,
    this.categoryLabel,
    this.openVinMode = false,
  });

  @override
  State<PartsScreen> createState() => _PartsScreenState();
}

class _PartsScreenState extends State<PartsScreen> {
  final _query = TextEditingController();
  final _repository = AppRepository();
  List<PartListingModel> _results = [];
  DecodedVehicleModel? _decodedVehicle;
  bool _loading = false;
  String? _error;
  String? _selectedCategory;
  String? _carYearId;
  bool _inStockOnly = true;
  _SearchMode _mode = _SearchMode.name;

  @override
  void initState() {
    super.initState();
    if (widget.openVinMode) _mode = _SearchMode.vin;
    if (widget.initialQuery != null) {
      _query.text = widget.initialQuery!;
    }
    _selectedCategory = widget.initialCategory;
    _carYearId = widget.initialCarYearId;
    if (_query.text.length >= 2 ||
        _selectedCategory != null ||
        _carYearId != null ||
        widget.initialCategoryId != null ||
        _mode == _SearchMode.vin) {
      _search();
    }
  }

  @override
  void dispose() {
    _query.dispose();
    super.dispose();
  }

  String? get _hint {
    switch (_mode) {
      case _SearchMode.name:
        return 'اسم القطعة أو الوصف…';
      case _SearchMode.oem:
        return 'رقم OEM المصنعي…';
      case _SearchMode.vin:
        return '17 رمزاً لرقم الهيكل (VIN)…';
    }
  }

  Future<void> _search() async {
    final q = _query.text.trim().toUpperCase();
    if (_mode == _SearchMode.vin) {
      if (q.length < 11) {
        setState(() => _error = 'أدخل 11 رمزاً على الأقل من رقم الهيكل');
        return;
      }
    } else if (q.length < 2 &&
        _selectedCategory == null &&
        _carYearId == null &&
        widget.initialCategoryId == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await _repository.searchParts(
        query: _mode == _SearchMode.name && q.isNotEmpty ? q : null,
        category: _selectedCategory,
        categoryId: widget.initialCategoryId,
        carYearId: _carYearId,
        oem: _mode == _SearchMode.oem && q.isNotEmpty ? q : null,
        vin: _mode == _SearchMode.vin ? q : null,
        inStockOnly: _inStockOnly,
      );
      setState(() {
        _results = result.parts;
        _decodedVehicle =
            _mode == _SearchMode.vin ? result.decodedVehicle : null;
        _loading = false;
        if (_mode == _SearchMode.vin && result.parts.isEmpty) {
          _error = result.decodedVehicle == null
              ? 'لم نتعرف على رقم الهيكل في قاعدة السوق الليبي'
              : 'لا توجد قطع OEM متوافقة مع هذا الهيكل';
        }
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.categoryLabel ?? 'بحث قطع الغيار'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SegmentedButton<_SearchMode>(
              segments: const [
                ButtonSegment(
                  value: _SearchMode.name,
                  label: Text('الاسم', style: TextStyle(fontSize: 12)),
                  icon: Icon(Icons.search, size: 16),
                ),
                ButtonSegment(
                  value: _SearchMode.oem,
                  label: Text('OEM', style: TextStyle(fontSize: 12)),
                  icon: Icon(Icons.tag, size: 16),
                ),
                ButtonSegment(
                  value: _SearchMode.vin,
                  label: Text('VIN', style: TextStyle(fontSize: 12)),
                  icon: Icon(Icons.directions_car, size: 16),
                ),
              ],
              selected: {_mode},
              onSelectionChanged: (s) {
                setState(() {
                  _mode = s.first;
                  _error = null;
                  _results = [];
                  _decodedVehicle = null;
                });
              },
            ),
            const SizedBox(height: 10),
            if (_mode == _SearchMode.vin)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.navy050,
                  borderRadius: AppDecorations.borderRadius,
                  border: Border.all(color: AppColors.navy.withValues(alpha: 0.12)),
                ),
                child: const Text(
                  'البحث برقم الهيكل: نطابق أول 11 رمزاً (WMI+VDS) مع القطع المسجّلة لضمان التوافق التام.',
                  style: TextStyle(fontSize: 11, color: AppColors.navy),
                ),
              ),
            if (_mode == _SearchMode.vin) const SizedBox(height: 8),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text(
                'متوفر في المخزون فقط',
                style: TextStyle(fontSize: 13, color: AppColors.navy),
              ),
              value: _inStockOnly,
              onChanged: (v) {
                setState(() => _inStockOnly = v);
                _search();
              },
            ),
            TextField(
              controller: _query,
              maxLength: _mode == _SearchMode.vin ? 17 : null,
              style: const TextStyle(color: AppColors.navy),
              inputFormatters: _mode == _SearchMode.vin
                  ? [
                      FilteringTextInputFormatter.allow(RegExp(r'[A-Za-z0-9]')),
                      UpperCaseTextFormatter(),
                    ]
                  : null,
              decoration: InputDecoration(
                hintText: _hint,
                prefixIcon: Icon(
                  _mode == _SearchMode.vin
                      ? Icons.qr_code_scanner
                      : Icons.search,
                  color: AppColors.navy,
                ),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward, color: AppColors.red),
                  onPressed: _search,
                ),
                counterText: _mode == _SearchMode.vin ? '17' : null,
              ),
              onSubmitted: (_) => _search(),
            ),
            if (_mode == _SearchMode.vin && _decodedVehicle != null)
              Container(
                margin: const EdgeInsets.only(top: 8),
                padding: const EdgeInsets.all(12),
                decoration: AppDecorations.vinMatchBadge(matched: true),
                child: Row(
                  children: [
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: AppColors.green.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.check_circle_outline,
                        color: AppColors.green,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'تطابق مع رقم الهيكل',
                            style: TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 12,
                              color: AppColors.navy,
                            ),
                          ),
                          Text(
                            _decodedVehicle!.labelAr,
                            style: const TextStyle(
                              fontWeight: FontWeight.w700,
                              fontSize: 13,
                              color: AppColors.navy,
                            ),
                          ),
                          if (_decodedVehicle!.engine != null)
                            Text(
                              _decodedVehicle!.engine!,
                              style: const TextStyle(
                                fontSize: 11,
                                color: AppColors.ink500,
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            if (_loading) const LinearProgressIndicator(),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  _error!,
                  style: const TextStyle(color: AppColors.red),
                ),
              ),
            Expanded(
              child: _results.isEmpty && !_loading
                  ? Center(
                      child: Text(
                        _mode == _SearchMode.vin
                            ? 'أدخل رقم الهيكل الكامل (17 رمزاً)'
                            : 'ابحث عن قطعة أو اختر تصنيفاً',
                        style: const TextStyle(color: AppColors.ink500),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _results.length,
                      itemBuilder: (context, i) => _PartCard(
                        part: _results[i],
                        showVinMatch: _mode == _SearchMode.vin,
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PartCard extends StatelessWidget {
  final PartListingModel part;
  final bool showVinMatch;

  const _PartCard({required this.part, this.showVinMatch = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(14),
      decoration: AppDecorations.card(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: AppColors.navy050,
                  borderRadius: AppDecorations.borderRadius,
                ),
                child: Icon(
                  part.isOem
                      ? Icons.verified_outlined
                      : Icons.inventory_2_outlined,
                  color: AppColors.navy,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      part.nameAr,
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 14,
                        color: AppColors.navy,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      part.partNumber,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.ink500,
                      ),
                    ),
                    if (showVinMatch && part.isOem)
                      Padding(
                        padding: const EdgeInsets.only(top: 6),
                        child: Row(
                          children: [
                            Icon(
                              Icons.check_circle,
                              size: 14,
                              color: AppColors.green,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              'متوافق مع الهيكل',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: AppColors.green,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              Text(
                formatAmount(part.priceSar),
                style: const TextStyle(
                  color: AppColors.navy,
                  fontWeight: FontWeight.w800,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 42,
            child: ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.add_shopping_cart_outlined, size: 18),
              label: const Text('أضف للسلة'),
            ),
          ),
        ],
      ),
    );
  }
}

class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    return newValue.copyWith(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
    );
  }
}
