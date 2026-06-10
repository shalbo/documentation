import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/registration_service.dart';
import '../theme/app_colors.dart';
import '../theme/app_decorations.dart';
import 'login_screen.dart';

class DriverRegisterScreen extends StatefulWidget {
  const DriverRegisterScreen({super.key});

  @override
  State<DriverRegisterScreen> createState() => _DriverRegisterScreenState();
}

class _DriverRegisterScreenState extends State<DriverRegisterScreen> {
  final _name = TextEditingController();
  final _phone = TextEditingController(text: '+2189');
  final _plate = TextEditingController();
  final _service = RegistrationService();
  final _picker = ImagePicker();

  int _step = 0;
  String? _city;
  String _serviceType = 'courier';
  List<String> _cities = [];
  String? _profileId;
  Uint8List? _license;
  Uint8List? _idDoc;
  Uint8List? _vehicle;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _service.fetchCities().then((c) => setState(() => _cities = c)).catchError((_) {
      setState(() => _cities = ['طرابلس', 'مصراتة', 'بنغازي']);
    });
  }

  @override
  void dispose() {
    _name.dispose();
    _phone.dispose();
    _plate.dispose();
    super.dispose();
  }

  Future<void> _pick(String kind) async {
    final file = await _picker.pickImage(source: ImageSource.gallery, imageQuality: 85);
    if (file == null) return;
    final bytes = await file.readAsBytes();
    setState(() {
      if (kind == 'license') _license = bytes;
      if (kind == 'id') _idDoc = bytes;
      if (kind == 'vehicle') _vehicle = bytes;
    });
  }

  Future<void> _nextStep() async {
    if (_step == 0) {
      if (_name.text.trim().length < 2 || _city == null || _plate.text.trim().isEmpty) {
        return;
      }
      setState(() => _loading = true);
      try {
        final res = await _service.registerDriverStep1(
          fullName: _name.text.trim(),
          phone: _phone.text.trim(),
          city: _city!,
          serviceType: _serviceType,
          plateNumber: _plate.text.trim(),
        );
        _profileId = (res['data'] as Map)['id'] as String;
        setState(() => _step = 1);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
        }
      } finally {
        if (mounted) setState(() => _loading = false);
      }
      return;
    }

    if (_license == null || _idDoc == null || _vehicle == null || _profileId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ارفع الرخصة والهوية وصورة السيارة')),
      );
      return;
    }
    setState(() => _loading = true);
    try {
      await _service.uploadDriverDocuments(
        profileId: _profileId!,
        licenseBytes: _license!,
        idBytes: _idDoc!,
        vehicleBytes: _vehicle!,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم إرسال الطلب — بانتظار اعتماد الإدارة')),
      );
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(title: Text('تسجيل سائق — خطوة ${_step + 1}/2')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            LinearProgressIndicator(value: (_step + 1) / 2),
            const SizedBox(height: 20),
            if (_step == 0) ...[
              TextField(
                controller: _name,
                decoration: const InputDecoration(labelText: 'الاسم الكامل'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _phone,
                decoration: const InputDecoration(labelText: 'رقم الجوال'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _city,
                decoration: const InputDecoration(labelText: 'المدينة'),
                items: _cities
                    .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                    .toList(),
                onChanged: (v) => setState(() => _city = v),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _serviceType,
                decoration: const InputDecoration(labelText: 'نوع الخدمة'),
                items: const [
                  DropdownMenuItem(
                    value: 'courier',
                    child: Text('مندوب قطع غيار'),
                  ),
                  DropdownMenuItem(
                    value: 'tow',
                    child: Text('سائق ساحبة أعطال'),
                  ),
                ],
                onChanged: (v) => setState(() => _serviceType = v ?? 'courier'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _plate,
                decoration: const InputDecoration(labelText: 'رقم اللوحة'),
              ),
            ] else ...[
              _DocTile(
                label: 'رخصة القيادة',
                done: _license != null,
                onTap: () => _pick('license'),
              ),
              const SizedBox(height: 10),
              _DocTile(
                label: 'الهوية الوطنية',
                done: _idDoc != null,
                onTap: () => _pick('id'),
              ),
              const SizedBox(height: 10),
              _DocTile(
                label: 'صورة السيارة',
                done: _vehicle != null,
                onTap: () => _pick('vehicle'),
              ),
            ],
            const Spacer(),
            SizedBox(
              height: 48,
              child: ElevatedButton(
                onPressed: _loading ? null : _nextStep,
                child: _loading
                    ? const CircularProgressIndicator(strokeWidth: 2)
                    : Text(_step == 0 ? 'التالي' : 'إرسال الطلب'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DocTile extends StatelessWidget {
  final String label;
  final bool done;
  final VoidCallback onTap;

  const _DocTile({
    required this.label,
    required this.done,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: AppDecorations.card(
          color: done ? AppColors.green050 : AppColors.surface,
        ),
        child: Row(
          children: [
            Icon(
              done ? Icons.check_circle : Icons.upload_file,
              color: done ? AppColors.green : AppColors.navy,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(label,
                  style: const TextStyle(
                      fontWeight: FontWeight.w700, color: AppColors.navy)),
            ),
            Text(done ? 'تم' : 'رفع',
                style: TextStyle(
                    color: done ? AppColors.green : AppColors.red,
                    fontWeight: FontWeight.w800)),
          ],
        ),
      ),
    );
  }
}
