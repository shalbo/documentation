import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_decorations.dart';
import 'customer_register_screen.dart';
import 'driver_register_screen.dart';
import 'login_screen.dart';

class RegisterRoleScreen extends StatelessWidget {
  const RegisterRoleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(title: const Text('إنشاء حساب')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'اختر نوع الحساب',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: AppColors.navy,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'سجّل كزبون أو سائق — التاجر والورشة عبر لوحة الويب',
              style: TextStyle(color: AppColors.ink500, fontSize: 13),
            ),
            const SizedBox(height: 24),
            _RoleCard(
              icon: Icons.person_outline,
              title: 'زبون',
              subtitle: 'شراء قطع غيار ومتابعة الطلبات',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const CustomerRegisterScreen()),
              ),
            ),
            const SizedBox(height: 12),
            _RoleCard(
              icon: Icons.local_shipping_outlined,
              title: 'سائق',
              subtitle: 'مندوب قطع غيار أو ساحبة أعطال',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const DriverRegisterScreen()),
              ),
            ),
            const Spacer(),
            TextButton(
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              ),
              child: const Text('لديك حساب؟ تسجيل الدخول'),
            ),
          ],
        ),
      ),
    );
  }
}

class _RoleCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _RoleCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: AppDecorations.card(),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.navy050,
                borderRadius: AppDecorations.borderRadius,
              ),
              child: Icon(icon, color: AppColors.navy),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                          color: AppColors.navy)),
                  Text(subtitle,
                      style: const TextStyle(
                          color: AppColors.ink500, fontSize: 12)),
                ],
              ),
            ),
            const Icon(Icons.chevron_left, color: AppColors.ink300),
          ],
        ),
      ),
    );
  }
}
