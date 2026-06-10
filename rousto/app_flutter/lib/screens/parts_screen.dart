import 'package:flutter/material.dart';

import '../data/app_repository.dart';
import '../data/models.dart';
import '../theme/app_colors.dart';
import '../currency.dart';

class PartsScreen extends StatefulWidget {
  final String? initialQuery;
  final String? initialCategory;
  final String? initialCarYearId;

  const PartsScreen({
    super.key,
    this.initialQuery,
    this.initialCategory,
    this.initialCarYearId,
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

  @override
  void initState() {
    super.initState();
    if (widget.initialQuery != null) {
      _query.text = widget.initialQuery!;
    }
    _selectedCategory = widget.initialCategory;
    _carYearId = widget.initialCarYearId;
    if (_query.text.length >= 2 ||
        _selectedCategory != null ||
        _carYearId != null) {
      _search();
    }
  }

  @override
  void dispose() {
    _query.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final q = _query.text.trim();
    final isOem = q.length >= 3 && RegExp(r'^[A-Z0-9-]+$').hasMatch(q.toUpperCase());
    final isVin = q.length >= 8;
    if (q.length < 2 &&
        _selectedCategory == null &&
        _carYearId == null &&
        !isOem &&
        !isVin) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final results = await _repository.searchParts(
        query: q.isNotEmpty && !isOem && !isVin ? q : null,
        category: _selectedCategory,
        carYearId: _carYearId,
        oem: isOem ? q.toUpperCase() : null,
        vin: isVin && q.length >= 11 ? q.toUpperCase() : null,
        inStockOnly: _inStockOnly,
      );
      setState(() {
        _results = results;
        _loading = false;
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
      appBar: AppBar(title: const Text('بحث قطع الغيار')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
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
              decoration: InputDecoration(
                hintText: 'OEM أو VIN أو اسم القطعة…',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: _search,
                ),
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
                  ? const Center(
                      child: Text(
                        'ابحث برقم القطعة أو اختر تصنيفاً',
                        style: TextStyle(color: AppColors.ink500),
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
