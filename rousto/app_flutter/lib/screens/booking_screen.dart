import 'package:flutter/material.dart';

import '../data/models.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';

class BookingScreen extends StatefulWidget {
  final ServiceItem? service;
  const BookingScreen({super.key, this.service});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  int _slot = 1;
  static const _slots = ['السبت', 'الأحد 9 ص', 'الاثنين', 'الثلاثاء'];

  @override
  Widget build(BuildContext context) {
    final s = widget.service ?? AppData.services.first;
    const discount = 30;
    final total = s.price - discount;

    return Scaffold(
      appBar: AppBar(title: const Text('تأكيد الحجز')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(18, 6, 18, 100),
          children: [
            SoftCard(
              color: AppColors.red050,
              child: Row(
                children: [
                  IconBadge(s.icon, bg: Colors.white),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(s.name,
                            style: const TextStyle(
                                fontWeight: FontWeight.w800, fontSize: 15)),
                        Text(s.subtitle,
                            style: const TextStyle(
                                color: AppColors.ink500, fontSize: 12)),
                      ],
                    ),
                  ),
                  Text('${s.price} ريال',
                      style: const TextStyle(
                          color: AppColors.red600,
                          fontWeight: FontWeight.w800)),
                ],
              ),
            ),
            const SizedBox(height: 18),
            const _Label('سيارتك'),
            const _InfoRow(
              icon: Icons.directions_car_filled_outlined,
              title: 'تويوتا كامري 2022',
              subtitle: 'أبيض · أ ب ج 1234',
            ),
            const SizedBox(height: 18),
            const _Label('الموعد'),
            SizedBox(
              height: 38,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _slots.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (_, i) {
                  final active = i == _slot;
                  return GestureDetector(
                    onTap: () => setState(() => _slot = i),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color:
                            active ? AppColors.red050 : AppColors.surface,
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(
                            color: active
                                ? Colors.transparent
                                : AppColors.line),
                      ),
                      child: Text(_slots[i],
                          style: TextStyle(
                            color: active
                                ? AppColors.red600
                                : AppColors.ink700,
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                          )),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 18),
            const _Label('المكان'),
            const _InfoRow(
              icon: Icons.location_on_outlined,
              title: 'خدمة في موقعك',
              subtitle: 'حي النخيل، الرياض',
            ),
            const SizedBox(height: 18),
            const _Label('طريقة الدفع'),
            const _InfoRow(
              icon: Icons.credit_card,
              title: 'مدى **** 4421',
              subtitle: 'بطاقة افتراضية',
            ),
            const SizedBox(height: 18),
            SoftCard(
              child: Column(
                children: [
                  _summaryRow('الخدمة', '${s.price} ريال'),
                  const SizedBox(height: 6),
                  _summaryRow('خصم (ROUSTO)', '- $discount ريال',
                      color: AppColors.green),
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8),
                    child: Divider(color: AppColors.line, height: 1),
                  ),
                  _summaryRow('الإجمالي', '$total ريال',
                      bold: true, color: AppColors.red600),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.fromLTRB(18, 0, 18, 18),
        child: GradientButton(
          label: 'تأكيد ودفع $total ريال',
          onPressed: () => _confirm(context),
        ),
      ),
    );
  }

  void _confirm(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.vertical(top: Radius.circular(26)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircleAvatar(
              radius: 34,
              backgroundColor: AppColors.green,
              child: Icon(Icons.check, color: Colors.white, size: 34),
            ),
            const SizedBox(height: 14),
            const Text('تم تأكيد حجزك!',
                style:
                    TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            const Text('سيتواصل معك فريق روستو لتأكيد التفاصيل.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.ink500)),
            const SizedBox(height: 18),
            GradientButton(
              label: 'تمام',
              onPressed: () {
                Navigator.of(context).pop();
                Navigator.of(context).pop();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _summaryRow(String label, String value,
      {bool bold = false, Color? color}) {
    final style = TextStyle(
      fontSize: bold ? 16 : 13,
      fontWeight: bold ? FontWeight.w800 : FontWeight.w500,
      color: color ?? AppColors.ink500,
    );
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: style.copyWith(
                color: bold ? AppColors.ink900 : AppColors.ink500)),
        Text(value, style: style),
      ],
    );
  }
}

class _Label extends StatelessWidget {
  final String text;
  const _Label(this.text);
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Text(text,
            style:
                const TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
      );
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  const _InfoRow(
      {required this.icon, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return SoftCard(
      child: Row(
        children: [
          IconBadge(icon, size: 40),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 14)),
                Text(subtitle,
                    style: const TextStyle(
                        color: AppColors.ink500, fontSize: 12)),
              ],
            ),
          ),
          const Icon(Icons.chevron_left, color: AppColors.ink300),
        ],
      ),
    );
  }
}
