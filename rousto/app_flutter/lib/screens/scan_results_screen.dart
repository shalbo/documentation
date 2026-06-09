import 'package:flutter/material.dart';

import '../data/models.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'booking_screen.dart';

class ScanResultsScreen extends StatelessWidget {
  final ScanModel scan;
  const ScanResultsScreen({super.key, required this.scan});

  Color _severityColor(String severity) {
    switch (severity) {
      case 'high':
        return AppColors.red600;
      case 'low':
        return AppColors.green;
      default:
        return const Color(0xFFF2B705);
    }
  }

  String _severityLabel(String severity) {
    switch (severity) {
      case 'high':
        return 'عالي';
      case 'low':
        return 'منخفض';
      default:
        return 'متوسط';
    }
  }

  @override
  Widget build(BuildContext context) {
    final finding = scan.primaryFinding;
    final service = finding?.suggestedService;

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        title: const Text('نتائج الفحص'),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.ink900,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 12, 18, 24),
        children: [
          SoftCard(
            child: Row(
              children: [
                const IconBadge(Icons.auto_awesome, size: 48),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('تم التحليل',
                          style: TextStyle(
                              fontWeight: FontWeight.w800, fontSize: 16)),
                      Text(
                        'دقة تقديرية ${((finding?.confidence ?? 0) * 100).round()}٪',
                        style: const TextStyle(
                            color: AppColors.ink500, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          for (final f in scan.findings) ...[
            SoftCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: _severityColor(f.severity).withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          'خطورة ${_severityLabel(f.severity)}',
                          style: TextStyle(
                            color: _severityColor(f.severity),
                            fontWeight: FontWeight.w800,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(f.labelAr,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 15)),
                  if (f.suggestedService != null) ...[
                    const SizedBox(height: 12),
                    const Divider(height: 1),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        IconBadge(f.suggestedService!.icon, size: 40),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('الخدمة المقترحة',
                                  style: TextStyle(
                                      color: AppColors.ink500, fontSize: 11)),
                              Text(f.suggestedService!.name,
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w800,
                                      fontSize: 14)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 10),
          ],
          if (service != null)
            GradientButton(
              label: 'احجز ${service.name}',
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => BookingScreen(
                      service: service,
                      scanId: scan.id.startsWith('mock') ? null : scan.id,
                    ),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }
}
