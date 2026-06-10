import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme/app_colors.dart';

typedef PaymentOtpGenerate = Future<Map<String, dynamic>> Function();
typedef PaymentOtpVerify = Future<Map<String, dynamic>> Function(String code);
typedef PaymentOtpResend = Future<Map<String, dynamic>> Function();

class PaymentOtpSheet extends StatefulWidget {
  final PaymentOtpGenerate onGenerate;
  final PaymentOtpVerify onVerify;
  final PaymentOtpResend onResend;
  final double? amountLyd;

  const PaymentOtpSheet({
    super.key,
    required this.onGenerate,
    required this.onVerify,
    required this.onResend,
    this.amountLyd,
  });

  static Future<Map<String, dynamic>?> show(
    BuildContext context, {
    required PaymentOtpGenerate onGenerate,
    required PaymentOtpVerify onVerify,
    required PaymentOtpResend onResend,
    double? amountLyd,
  }) {
    return showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => PaymentOtpSheet(
        onGenerate: onGenerate,
        onVerify: onVerify,
        onResend: onResend,
        amountLyd: amountLyd,
      ),
    );
  }

  @override
  State<PaymentOtpSheet> createState() => _PaymentOtpSheetState();
}

class _PaymentOtpSheetState extends State<PaymentOtpSheet> {
  final _codeCtrl = TextEditingController();
  int _secondsLeft = 60;
  Timer? _timer;
  bool _loading = false;
  String? _error;
  String? _devOtp;

  @override
  void initState() {
    super.initState();
    _startGenerate();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _codeCtrl.dispose();
    super.dispose();
  }

  void _startCountdown() {
    _timer?.cancel();
    setState(() => _secondsLeft = 60);
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_secondsLeft <= 1) {
        t.cancel();
        setState(() => _secondsLeft = 0);
      } else {
        setState(() => _secondsLeft -= 1);
      }
    });
  }

  Future<void> _startGenerate() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final res = await widget.onGenerate();
      final meta = res['meta'] as Map<String, dynamic>?;
      setState(() {
        _devOtp = meta?['dev_otp'] as String?;
        if (_devOtp != null) _codeCtrl.text = _devOtp!;
      });
      _startCountdown();
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _resend() async {
    if (_secondsLeft > 0) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final res = await widget.onResend();
      final meta = res['meta'] as Map<String, dynamic>?;
      setState(() {
        _devOtp = meta?['dev_otp'] as String?;
        if (_devOtp != null) _codeCtrl.text = _devOtp!;
      });
      _startCountdown();
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _verify() async {
    final code = _codeCtrl.text.trim();
    if (code.length < 4) {
      setState(() => _error = 'أدخل الرمز المكوّن من 4 أرقام');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await widget.onVerify(code);
      if (!mounted) return;
      Navigator.of(context).pop(result);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.fromLTRB(22, 20, 22, 24),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.line),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.red050,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.lock_outline, color: AppColors.red),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'تأكيد العملية المالية',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 17,
                          color: AppColors.navy,
                        ),
                      ),
                      if (widget.amountLyd != null)
                        Text(
                          '${widget.amountLyd!.toStringAsFixed(2)} د.ل',
                          style: const TextStyle(color: AppColors.red, fontWeight: FontWeight.w700),
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'أدخل الرمز المرسل إلى هاتفك لإتمام الدفع',
              style: TextStyle(color: AppColors.ink500, fontSize: 13),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _codeCtrl,
              keyboardType: TextInputType.number,
              textAlign: TextAlign.center,
              maxLength: 4,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w800,
                letterSpacing: 12,
                color: AppColors.navy,
              ),
              decoration: InputDecoration(
                counterText: '',
                hintText: '••••',
                filled: true,
                fillColor: AppColors.navy050,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: BorderSide.none,
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: const BorderSide(color: AppColors.red, width: 2),
                ),
                helperText: _devOtp != null ? 'وضع التطوير: $_devOtp' : null,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  _secondsLeft > 0
                      ? 'إعادة الإرسال خلال $_secondsLeft ث'
                      : 'يمكنك إعادة إرسال الرمز',
                  style: const TextStyle(fontSize: 12, color: AppColors.ink500),
                ),
                TextButton(
                  onPressed: _secondsLeft == 0 && !_loading ? _resend : null,
                  child: const Text('إعادة إرسال', style: TextStyle(color: AppColors.red)),
                ),
              ],
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(_error!, style: const TextStyle(color: AppColors.red, fontSize: 13)),
              ),
            SizedBox(
              height: 48,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.red,
                  foregroundColor: Colors.white,
                ),
                onPressed: _loading ? null : _verify,
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('تأكيد ودفع الحساب'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
