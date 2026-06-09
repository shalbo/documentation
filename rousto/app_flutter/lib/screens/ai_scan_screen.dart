import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../data/app_repository.dart';
import '../data/models.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'scan_results_screen.dart';

class AiScanScreen extends StatefulWidget {
  const AiScanScreen({super.key});

  @override
  State<AiScanScreen> createState() => _AiScanScreenState();
}

class _AiScanScreenState extends State<AiScanScreen> {
  final _repository = AppRepository();
  final _picker = ImagePicker();

  bool _loading = true;
  bool _submitting = false;
  List<ScanTypeModel> _types = [];
  int _selectedType = 0;
  Uint8List? _imageBytes;
  String? _imageName;
  VehicleModel? _vehicle;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final types = await _repository.loadScanTypes();
    final contextData = await _repository.loadBookingContext();
    setState(() {
      _types = types;
      _vehicle = contextData.vehicle;
      _loading = false;
    });
  }

  Future<void> _pickImage() async {
    final picked = await _picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1600,
      imageQuality: 85,
    );
    if (picked == null) return;
    final bytes = await picked.readAsBytes();
    setState(() {
      _imageBytes = bytes;
      _imageName = picked.name;
    });
  }

  Future<void> _submit() async {
    if (_imageBytes == null || _vehicle == null || _types.isEmpty) return;
    setState(() => _submitting = true);
    try {
      final scan = await _repository.submitScan(
        vehicleId: _vehicle!.id,
        scanType: _types[_selectedType].id,
        imageBytes: _imageBytes!,
        filename: _imageName ?? 'scan.jpg',
      );
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => ScanResultsScreen(scan: scan)),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        title: const Text('فحص بالصورة'),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.ink900,
        elevation: 0,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(18, 12, 18, 24),
              children: [
                const Eyebrow('ذكاء اصطناعي'),
                const SizedBox(height: 8),
                const Text(
                  'التقط صورة للمشكلة واحصل على تشخيص مبدئي وخدمة مقترحة',
                  style: TextStyle(color: AppColors.ink500, fontSize: 14),
                ),
                const SizedBox(height: 18),
                const Text('نوع الفحص',
                    style: TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
                const SizedBox(height: 10),
                ...List.generate(_types.length, (i) {
                  final t = _types[i];
                  final active = i == _selectedType;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: GestureDetector(
                      onTap: () => setState(() => _selectedType = i),
                      child: SoftCard(
                        child: Row(
                          children: [
                            IconBadge(
                              t.icon,
                              bg: active ? AppColors.red050 : AppColors.cream,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(t.labelAr,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 14)),
                                  Text(t.descriptionAr,
                                      style: const TextStyle(
                                          color: AppColors.ink500,
                                          fontSize: 12)),
                                ],
                              ),
                            ),
                            if (active)
                              const Icon(Icons.check_circle,
                                  color: AppColors.red600),
                          ],
                        ),
                      ),
                    ),
                  );
                }),
                const SizedBox(height: 12),
                SoftCard(
                  child: Column(
                    children: [
                      if (_imageBytes != null)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.memory(
                            _imageBytes!,
                            height: 180,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        )
                      else
                        Container(
                          height: 140,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            color: AppColors.cream,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppColors.line),
                          ),
                          child: const Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.add_a_photo_outlined,
                                  color: AppColors.ink300, size: 36),
                              SizedBox(height: 8),
                              Text('لم تُختَر صورة بعد',
                                  style: TextStyle(color: AppColors.ink500)),
                            ],
                          ),
                        ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: _pickImage,
                              icon: const Icon(Icons.photo_library_outlined),
                              label: const Text('اختيار صورة'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                GradientButton(
                  label: _submitting ? 'جاري التحليل...' : 'تحليل الصورة',
                  onPressed:
                      (_imageBytes == null || _submitting) ? null : _submit,
                ),
              ],
            ),
    );
  }
}
