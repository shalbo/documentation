import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/app_repository.dart';
import '../data/models.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';

class TrackingScreen extends StatefulWidget {
  final String? bookingId;
  const TrackingScreen({super.key, this.bookingId});

  @override
  State<TrackingScreen> createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  bool _loading = true;
  BookingModel? _booking;
  TechnicianModel? _technician;
  List<TrackStepModel> _steps = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final state = context.read<AppState>();
    final bookingId = widget.bookingId ?? state.activeBooking?.id;
    if (bookingId == null) {
      setState(() => _loading = false);
      return;
    }

    final repo = AppRepository();
    final result = await repo.loadTracking(bookingId);
    setState(() {
      _booking = result.booking;
      _technician = result.technician;
      _steps = result.steps;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        backgroundColor: AppColors.bg,
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_booking == null) {
      return Scaffold(
        backgroundColor: AppColors.bg,
        body: SafeArea(
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.receipt_long_outlined,
                    size: 48, color: AppColors.ink300),
                const SizedBox(height: 12),
                const Text('لا يوجد حجز جاري',
                    style:
                        TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                const SizedBox(height: 16),
                GradientButton(label: 'تحديث', onPressed: _load),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.bg,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 110),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('تتبّع الخدمة',
                    style: TextStyle(
                        fontSize: 20, fontWeight: FontWeight.w800)),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF3D6),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    _booking!.statusLabelAr,
                    style: const TextStyle(
                        color: Color(0xFFB07D00),
                        fontWeight: FontWeight.w800,
                        fontSize: 12),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            _map(),
            const SizedBox(height: 14),
            if (_technician != null) _technicianCard(_technician!),
            const SizedBox(height: 14),
            _stepsCard(),
            const SizedBox(height: 14),
            GradientButton(
              label: 'مراسلة الفني',
              icon: Icons.chat_bubble_outline,
              gradient: const LinearGradient(
                  colors: [AppColors.ink900, AppColors.ink700]),
              onPressed: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _map() {
    return Container(
      height: 160,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: const LinearGradient(
          colors: [Color(0xFFD8E8DD), Color(0xFFCFE0EA)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: 90,
            left: -20,
            right: -20,
            child: Transform.rotate(
              angle: -0.1,
              child: Container(
                height: 14,
                color: Colors.white.withValues(alpha: 0.85),
              ),
            ),
          ),
          const Align(
            alignment: Alignment(0.2, -0.1),
            child: CircleAvatar(
              radius: 20,
              backgroundColor: AppColors.red,
              child: Icon(Icons.local_shipping_outlined,
                  color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }

  Widget _technicianCard(TechnicianModel tech) {
    return SoftCard(
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: AppColors.red,
            child: Text(
              tech.avatarInitials ?? tech.fullName.substring(0, 1),
              style: const TextStyle(
                  color: Colors.white, fontWeight: FontWeight.w800),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tech.fullName,
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 14)),
                Text(tech.subtitle,
                    style: const TextStyle(
                        color: AppColors.ink500, fontSize: 12)),
              ],
            ),
          ),
          const CircleAvatar(
            radius: 20,
            backgroundColor: AppColors.green,
            child: Icon(Icons.call, color: Colors.white, size: 18),
          ),
        ],
      ),
    );
  }

  Widget _stepsCard() {
    return SoftCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          for (int i = 0; i < _steps.length; i++)
            _StepRow(step: _steps[i], isLast: i == _steps.length - 1),
        ],
      ),
    );
  }
}

class _StepRow extends StatelessWidget {
  final TrackStepModel step;
  final bool isLast;
  const _StepRow({required this.step, required this.isLast});

  @override
  Widget build(BuildContext context) {
    final color = trackStatusColor(step.status);
    final icon = step.status == TrackStatus.done
        ? Icons.check
        : step.status == TrackStatus.current
            ? Icons.circle
            : Icons.circle_outlined;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            children: [
              Container(
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  color: step.status == TrackStatus.todo
                      ? AppColors.line
                      : color,
                  shape: BoxShape.circle,
                ),
                child: Icon(icon,
                    size: 12,
                    color: step.status == TrackStatus.todo
                        ? AppColors.ink300
                        : Colors.white),
              ),
              if (!isLast)
                Expanded(
                  child: Container(width: 2, color: AppColors.line),
                ),
            ],
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: isLast ? 0 : 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(step.title,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 14)),
                  Text(step.time,
                      style: const TextStyle(
                          color: AppColors.ink500, fontSize: 12)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
