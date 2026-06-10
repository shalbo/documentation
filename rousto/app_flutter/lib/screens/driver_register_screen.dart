import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../services/registration_service.dart';
import '../theme/app_colors.dart';
import '../theme/app_decorations.dart';
import '../widgets/payment_otp_sheet.dart';
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
  String _serviceType = 'tow';
  String _vehicleType = 'tow_truck';
  List<String> _cities = [];
  String? _profileId;
  Uint8List? _license;
  Uint8List? _idDoc;
  Uint8List? _vehicle;
  bool _loading = false;
  String? _paymentError;
  double _registrationFee = 150;
  bool _paymentComplete = false;

  bool get _requiresPayment => _serviceType == 'tow';
  int get _totalSteps => _requiresPayment ? 3 : 2;

  @override
  void initState() {
    super.initState();
    _service.fetchCities().then((c) => setState(() => _cities = c)).catchError((_) {
      setState(() => _cities = ['طرابلس', 'مصراتة', 'بنغازي']);
    });
    _service.fetchDriverRegistrationFee().then((fee) {
      if (mounted) setState(() => _registrationFee = fee);
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
      if (_requiresPayment && _vehicleType.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('اختر نوع الآلية (ساحبة أو رافعة)')),
        );
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
          vehicleType: _requiresPayment ? _vehicleType : null,
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

    if (_step == 1) {
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
        if (_requiresPayment) {
          setState(() => _step = 2);
        } else {
          _showSuccessAndExit();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
        }
      } finally {
        if (mounted) setState(() => _loading = false);
      }
      return;
    }
  }

  Future<void> _payWithGateway(String gateway) async {
    if (_profileId == null) return;
    setState(() {
      _loading = true;
      _paymentError = null;
    });
    try {
      final res = await _service.initiateDriverRegistrationPayment(
        profileId: _profileId!,
        phone: _phone.text.trim(),
        gateway: gateway,
      );
      final data = res['data'] as Map<String, dynamic>? ?? res;
      if (data['already_paid'] == true) {
        setState(() => _paymentComplete = true);
        _showSuccessAndExit();
        return;
      }
      final orderId = (data['order_id'] ?? data['intent_id']) as String?;
      if (orderId == null) {
        throw Exception('لم يُنشأ طلب الدفع');
      }
      if (!mounted) return;
      setState(() => _loading = false);

      final verified = await PaymentOtpSheet.show(
        context,
        amountLyd: _registrationFee,
        onGenerate: () => _service.generateRegistrationPaymentOtp(
          orderId: orderId,
          phone: _phone.text.trim(),
          amountLyd: _registrationFee,
        ),
        onResend: () => _service.generateRegistrationPaymentOtp(
          orderId: orderId,
          phone: _phone.text.trim(),
          amountLyd: _registrationFee,
        ),
        onVerify: (code) => _service.verifyRegistrationPaymentOtp(
          orderId: orderId,
          phone: _phone.text.trim(),
          code: code,
        ),
      );
      if (verified == null) {
        setState(() => _paymentError = 'لم يكتمل تأكيد الرمز المالي');
        return;
      }

      final verifiedData = verified['data'] as Map<String, dynamic>? ?? verified;
      final redirect = verifiedData['redirect_url'] as String?;
      if (redirect == null) {
        final paid = await _pollPaymentConfirmed();
        if (paid) {
          setState(() => _paymentComplete = true);
          _showSuccessAndExit();
        }
        return;
      }
      final webviewOk = await Navigator.of(context).push<bool>(
        MaterialPageRoute(builder: (_) => _DriverPaymentWebView(url: redirect)),
      );
      if (webviewOk != true) {
        setState(() => _paymentError = 'لم تكتمل عملية الدفع — يمكنك إعادة المحاولة');
        return;
      }
      final paid = await _pollPaymentConfirmed();
      if (paid) {
        setState(() => _paymentComplete = true);
        _showSuccessAndExit();
      } else {
        setState(() => _paymentError = 'بانتظار تأكيد الدفع من البنك — أعد المحاولة بعد قليل');
      }
    } catch (e) {
      setState(() => _paymentError = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<bool> _pollPaymentConfirmed() async {
    for (var i = 0; i < 15; i++) {
      await Future<void>.delayed(const Duration(seconds: 2));
      final status = await _service.getDriverPaymentStatus(
        profileId: _profileId!,
        phone: _phone.text.trim(),
      );
      final data = status['data'] as Map<String, dynamic>;
      if (data['registration_fee_status'] == 'paid') {
        return true;
      }
    }
    return false;
  }

  void _showSuccessAndExit() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم تقديم طلبك بنجاح — بانتظار مراجعة الإدارة'),
      ),
    );
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(title: Text('تسجيل سائق — خطوة ${_step + 1}/$_totalSteps')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            LinearProgressIndicator(value: (_step + 1) / _totalSteps),
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
                onChanged: (v) => setState(() => _serviceType = v ?? 'tow'),
              ),
              if (_requiresPayment) ...[
                const SizedBox(height: 20),
                const Text(
                  'بيانات المركبة',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 15,
                    color: AppColors.navy,
                  ),
                ),
                const SizedBox(height: 10),
                _VehicleTypeOption(
                  value: 'tow_truck',
                  groupValue: _vehicleType,
                  title: 'ساحبة عادية',
                  subtitle: 'سحب المركبة المعطلة بالخطاف',
                  accentColor: AppColors.red,
                  onChanged: (v) => setState(() => _vehicleType = v!),
                ),
                const SizedBox(height: 8),
                _VehicleTypeOption(
                  value: 'flatbed',
                  groupValue: _vehicleType,
                  title: 'رافعة (سطحة)',
                  subtitle: 'نقل المركبة على منصة مسطحة',
                  accentColor: AppColors.navy,
                  onChanged: (v) => setState(() => _vehicleType = v!),
                ),
              ],
              const SizedBox(height: 12),
              TextField(
                controller: _plate,
                decoration: const InputDecoration(labelText: 'رقم اللوحة'),
              ),
            ] else if (_step == 1) ...[
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
            ] else ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: AppDecorations.card(color: AppColors.red050),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'رسوم تفعيل الحساب',
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 16,
                        color: AppColors.navy,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${_registrationFee.toStringAsFixed(2)} دينار ليبي',
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: AppColors.red,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'الدفع إلزامي لتفعيل حساب سائق الساحبة ومراجعته من الإدارة.',
                      style: TextStyle(color: AppColors.ink500, fontSize: 13),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _PaymentOptionTile(
                label: 'بطاقة معاملات',
                subtitle: 'مصرف الجمهورية — OTP',
                icon: Icons.credit_card,
                onTap: _loading ? null : () => _payWithGateway('muamalat'),
              ),
              const SizedBox(height: 10),
              _PaymentOptionTile(
                label: 'تطبيق سداد',
                subtitle: 'المدار الجديد — دفع موبايل',
                icon: Icons.phone_android,
                onTap: _loading ? null : () => _payWithGateway('sadad'),
              ),
              if (_paymentError != null) ...[
                const SizedBox(height: 12),
                Text(
                  _paymentError!,
                  style: const TextStyle(color: AppColors.red, fontSize: 13),
                ),
              ],
              if (_paymentComplete) ...[
                const SizedBox(height: 12),
                const Row(
                  children: [
                    Icon(Icons.check_circle, color: AppColors.green),
                    SizedBox(width: 8),
                    Text('تم سداد الرسوم بنجاح', style: TextStyle(color: AppColors.green)),
                  ],
                ),
              ],
            ],
            const Spacer(),
            if (_step < 2)
              SizedBox(
                height: 48,
                child: ElevatedButton(
                  onPressed: _loading ? null : _nextStep,
                  child: _loading
                      ? const CircularProgressIndicator(strokeWidth: 2)
                      : Text(_step == 0 ? 'التالي' : 'التالي — الدفع'),
                ),
              ),
            if (_step == 2 && _loading)
              const Center(child: CircularProgressIndicator()),
          ],
        ),
      ),
    );
  }
}

class _VehicleTypeOption extends StatelessWidget {
  final String value;
  final String groupValue;
  final String title;
  final String subtitle;
  final Color accentColor;
  final ValueChanged<String?> onChanged;

  const _VehicleTypeOption({
    required this.value,
    required this.groupValue,
    required this.title,
    required this.subtitle,
    required this.accentColor,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final selected = value == groupValue;
    return Material(
      color: selected ? accentColor.withValues(alpha: 0.08) : AppColors.surface,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => onChanged(value),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: selected ? accentColor : AppColors.line,
              width: selected ? 2 : 1,
            ),
          ),
          child: Row(
            children: [
              Radio<String>(
                value: value,
                groupValue: groupValue,
                activeColor: accentColor,
                onChanged: onChanged,
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                        color: selected ? accentColor : AppColors.navy,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.ink500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
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

class _PaymentOptionTile extends StatelessWidget {
  final String label;
  final String subtitle;
  final IconData icon;
  final VoidCallback? onTap;

  const _PaymentOptionTile({
    required this.label,
    required this.subtitle,
    required this.icon,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surface,
      borderRadius: BorderRadius.circular(14),
      child: ListTile(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: const BorderSide(color: AppColors.line),
        ),
        leading: Icon(icon, color: AppColors.navy),
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_back_ios, size: 16, color: AppColors.navy),
        onTap: onTap,
      ),
    );
  }
}

class _DriverPaymentWebView extends StatefulWidget {
  final String url;
  const _DriverPaymentWebView({required this.url});

  @override
  State<_DriverPaymentWebView> createState() => _DriverPaymentWebViewState();
}

class _DriverPaymentWebViewState extends State<_DriverPaymentWebView> {
  late final WebViewController _controller;
  bool _done = false;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (url) {
            if (url.contains('success') || url.contains('rousto://payment/return')) {
              if (!_done) {
                _done = true;
                Navigator.of(context).pop(true);
              }
            }
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('بوابة الدفع الآمنة')),
      body: WebViewWidget(controller: _controller),
    );
  }
}
