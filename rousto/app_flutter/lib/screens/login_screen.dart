import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../services/auth_service.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import 'root_nav.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneCtrl = TextEditingController(text: '+966501234567');
  final _codeCtrl = TextEditingController();
  final _auth = AuthService();
  bool _otpSent = false;
  bool _loading = false;
  String? _devOtp;

  @override
  void dispose() {
    _phoneCtrl.dispose();
    _codeCtrl.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    setState(() => _loading = true);
    try {
      final dev = await _auth.sendOtp(_phoneCtrl.text.trim());
      setState(() {
        _otpSent = true;
        _devOtp = dev.isNotEmpty ? dev : null;
        if (_devOtp != null) _codeCtrl.text = _devOtp!;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(AppLocalizations.of(context)!.codeSent)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _verify() async {
    setState(() => _loading = true);
    try {
      await _auth.verifyOtp(
        phone: _phoneCtrl.text.trim(),
        code: _codeCtrl.text.trim(),
      );
      if (!mounted) return;
      await context.read<AppState>().load();
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const RootNav()),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(title: Text(l10n.login)),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _phoneCtrl,
              keyboardType: TextInputType.phone,
              decoration: InputDecoration(labelText: l10n.phoneNumber),
            ),
            const SizedBox(height: 16),
            if (_otpSent) ...[
              TextField(
                controller: _codeCtrl,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: l10n.verificationCode,
                  helperText: _devOtp != null
                      ? l10n.devOtpHelper(_devOtp!)
                      : null,
                ),
              ),
              const SizedBox(height: 16),
            ],
            ElevatedButton(
              onPressed: _loading ? null : (_otpSent ? _verify : _sendOtp),
              child: _loading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(_otpSent ? l10n.confirmLogin : l10n.sendCode),
            ),
          ],
        ),
      ),
    );
  }
}
