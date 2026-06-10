import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../api/api_client.dart';
import '../config/app_config.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'parts_screen.dart';

class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  final _api = ApiClient(baseUrl: AppConfig.apiBaseUrl);
  List<Map<String, dynamic>> _roots = [];
  bool _loading = true;

  static const _mockRoots = [
    {
      'id': 'r1',
      'slug': 'cat-filters',
      'name_ar': 'فلاتر وزيوت',
      'icon_key': 'filters',
    },
    {
      'id': 'r2',
      'slug': 'cat-brakes',
      'name_ar': 'فرامل وتعليق',
      'icon_key': 'brakes',
    },
    {
      'id': 'r3',
      'slug': 'cat-electrical',
      'name_ar': 'كهرباء وبطاريات',
      'icon_key': 'electrical',
    },
    {
      'id': 'r4',
      'slug': 'cat-engines',
      'name_ar': 'محرك وناقل',
      'icon_key': 'engine',
    },
    {
      'id': 'r5',
      'slug': 'cat-belts',
      'name_ar': 'سيور ومضخات',
      'icon_key': 'belts',
    },
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await _api.getCategoryRoots();
      setState(() {
        _roots = data;
        _loading = false;
      });
    } catch (_) {
      setState(() {
        _roots = _mockRoots;
        _loading = false;
      });
    }
  }

  IconData _icon(String? key) {
    switch (key) {
      case 'engine':
        return Icons.precision_manufacturing_outlined;
      case 'brakes':
        return Icons.disc_full_outlined;
      case 'filters':
        return Icons.filter_alt_outlined;
      case 'electrical':
        return Icons.electric_bolt_outlined;
      case 'belts':
        return Icons.settings_suggest_outlined;
      default:
        return Icons.category_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    final fitment = context.watch<AppState>().fitment;

    return Scaffold(
      appBar: AppBar(
        title: const Text('الكتالوج'),
        actions: [
          if (fitment?.isComplete == true)
            Padding(
              padding: const EdgeInsets.only(left: 12),
              child: Center(
                child: Text(
                  fitment!.label,
                  style: const TextStyle(fontSize: 11),
                ),
              ),
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: GridView.builder(
                padding: const EdgeInsets.all(18),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 14,
                  mainAxisSpacing: 14,
                  childAspectRatio: 0.95,
                ),
                itemCount: _roots.length,
                itemBuilder: (_, i) {
                  final root = _roots[i];
                  return GestureDetector(
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => CatalogSubcategoriesScreen(
                          parentId: root['id'] as String,
                          parentName:
                              (root['name_ar'] ?? root['name']).toString(),
                          carYearId: fitment?.carYearId,
                        ),
                      ),
                    ),
                    child: SoftCard(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          IconBadge(
                            _icon(root['icon_key'] as String?),
                            size: 56,
                            bg: AppColors.navy050,
                            fg: AppColors.navy,
                          ),
                          const SizedBox(height: 14),
                          Text(
                            (root['name_ar'] ?? root['name']).toString(),
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 15,
                              color: AppColors.navy,
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'الأقسام الفرعية ←',
                            style: TextStyle(
                              color: AppColors.ink500,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
    );
  }
}

class CatalogSubcategoriesScreen extends StatefulWidget {
  final String parentId;
  final String parentName;
  final String? carYearId;

  const CatalogSubcategoriesScreen({
    super.key,
    required this.parentId,
    required this.parentName,
    this.carYearId,
  });

  @override
  State<CatalogSubcategoriesScreen> createState() =>
      _CatalogSubcategoriesScreenState();
}

class _CatalogSubcategoriesScreenState extends State<CatalogSubcategoriesScreen> {
  final _api = ApiClient(baseUrl: AppConfig.apiBaseUrl);
  List<Map<String, dynamic>> _children = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await _api.getCategoryChildren(widget.parentId);
      setState(() {
        _children = data;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.parentName)),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _children.isEmpty
              ? const Center(child: Text('لا توجد أقسام فرعية'))
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _children.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (_, i) {
                    final c = _children[i];
                    return ListTile(
                      tileColor: AppColors.surface,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                        side: const BorderSide(color: AppColors.line),
                      ),
                      leading: const Icon(Icons.inventory_2_outlined,
                          color: AppColors.navy),
                      title: Text(
                        (c['name_ar'] ?? c['name']).toString(),
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          color: AppColors.navy,
                        ),
                      ),
                      trailing: const Icon(Icons.chevron_left),
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => PartsScreen(
                              initialCategoryId: c['id'] as String,
                              initialCarYearId: widget.carYearId,
                              categoryLabel:
                                  (c['name_ar'] ?? c['name']).toString(),
                            ),
                          ),
                        );
                      },
                    );
                  },
                ),
    );
  }
}
