import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../data/app_repository.dart';
import '../data/models.dart';
import '../theme/app_colors.dart';
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
      final results = await _repository.searchParts(
        query: _mode == _SearchMode.name && q.isNotEmpty ? q : null,
        category: _selectedCategory,
        categoryId: widget.initialCategoryId,
        carYearId: _carYearId,
        oem: _mode == _SearchMode.oem && q.isNotEmpty ? q : null,
        vin: _mode == _SearchMode.vin ? q : null,
        inStockOnly: _inStockOnly,
      );
      setState(() {
        _results = results;
        _loading = false;
        if (_mode == _SearchMode.vin && results.isEmpty) {
          _error = 'لا توجد قطع OEM متوافقة مع هذا الهيكل';
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
                });
              },
            ),
            const SizedBox(height: 10),
            if (_mode == _SearchMode.vin)
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.red050,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Text(
                  'البحث برقم الهيكل: نطابق أول 11 رمزاً (WMI+VDS) مع القطع المسجّلة لضمان التوافق التام.',
                  style: TextStyle(fontSize: 11, color: AppColors.red600),
                ),
              ),
            if (_mode == _SearchMode.vin) const SizedBox(height: 8),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('متوفر في المخزون فقط', style: TextStyle(fontSize: 13)),
              value: _inStockOnly,
              onChanged: (v) {
                setState(() => _inStockOnly = v);
                _search();
              },
            ),
            TextField(
              controller: _query,
              maxLength: _mode == _SearchMode.vin ? 17 : null,
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
                ),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: _search,
                ),
                counterText: _mode == _SearchMode.vin ? '17' : null,
              ),
              onSubmitted: (_) => _search(),
            ),
            if (_loading) const LinearProgressIndicator(),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
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
                      itemBuilder: (context, i) {
                        final p = _results[i];
                        return Card(
                          margin: const EdgeInsets.only(top: 8),
                          child: ListTile(
                            leading: p.isOem
                                ? const Icon(Icons.verified_outlined,
                                    color: AppColors.red)
                                : const Icon(Icons.inventory_2_outlined),
                            title: Text(p.nameAr),
                            subtitle: Text(p.partNumber),
                            trailing: Text(
                              formatAmount(p.priceSar),
                              style: const TextStyle(
                                color: AppColors.red,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
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
