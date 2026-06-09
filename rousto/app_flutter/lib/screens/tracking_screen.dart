import 'dart:async';

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
  Timer? _pollTimer;
  bool _loading = true;
  BookingModel? _booking;
  TechnicianModel? _technician;
  TrackingDestinationModel? _destination;
  double? _distanceKm;
  double? _progressPercent;
  String? _deliveryPhaseLabel;
  List<DeliveryTrailPointModel> _trail = [];
  int _refreshSeconds = 20;
  List<TrackStepModel> _steps = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  void _schedulePolling(String? status, {int? refreshSeconds}) {
    _pollTimer?.cancel();
    if (status == 'en_route' || status == 'technician_assigned') {
      final seconds = refreshSeconds ?? _refreshSeconds;
      _pollTimer = Timer.periodic(Duration(seconds: seconds), (_) => _load());
    }
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() => _loading = _booking == null);

    final state = context.read<AppState>();
    final bookingId = widget.bookingId ?? state.activeBooking?.id;
    if (bookingId == null) {
      if (mounted) setState(() => _loading = false);
      return;
    }

    final repo = AppRepository();
    final result = await repo.loadTracking(bookingId);
    if (!mounted) return;

    setState(() {
      _booking = result.booking;
      _technician = result.technician;
      _destination = result.destination;
      _distanceKm = result.distanceKm;
      _progressPercent = result.progressPercent;
      _deliveryPhaseLabel = result.deliveryPhaseLabelAr;
      _trail = result.trail;
      if (result.refreshIntervalSeconds != null) {
        _refreshSeconds = result.refreshIntervalSeconds!;
      }
      _steps = result.steps;
      _loading = false;
    });
    _schedulePolling(
      result.booking.status,
      refreshSeconds: result.refreshIntervalSeconds,
    );
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
        child: RefreshIndicator(
          onRefresh: _load,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(18, 8, 18, 110),
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('تتبّع الخدمة',
                      style: TextStyle(
                          fontSize: 20, fontWeight: FontWeight.w800)),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFF3D6),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      _deliveryPhaseLabel ?? _booking!.statusLabelAr,
                      style: const TextStyle(
                          color: Color(0xFFB07D00),
                          fontWeight: FontWeight.w800,
                          fontSize: 12),
                    ),
                  ),
                ],
              ),
              if (_progressPercent != null) ...[
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(999),
                        child: LinearProgressIndicator(
                          value: (_progressPercent! / 100).clamp(0.0, 1.0),
                          minHeight: 8,
                          backgroundColor: AppColors.line,
                          color: AppColors.green,
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      '${_progressPercent!.toStringAsFixed(0)}%',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 12,
                        color: AppColors.ink500,
                      ),
                    ),
                  ],
                ),
              ],
              if (_distanceKm != null) ...[
                const SizedBox(height: 8),
                Text(
                  'المسافة ${_distanceKm!.toStringAsFixed(1)} كم'
                  '${_technician?.etaMinutes != null ? ' · يصل خلال ${_technician!.etaMinutes} دقيقة' : ''}',
                  style: const TextStyle(color: AppColors.ink500, fontSize: 12),
                ),
              ],
              const SizedBox(height: 14),
              _map(_technician?.location, _destination, _trail),
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
      ),
    );
  }

  Widget _map(
    GeoLocationModel? tech,
    TrackingDestinationModel? dest,
    List<DeliveryTrailPointModel> trail,
  ) {
    Alignment techAlign = const Alignment(0.2, -0.1);
    Alignment destAlign = const Alignment(-0.5, 0.4);
    final trailAlignments = <Alignment>[];

    final points = <({double lat, double lng})>[];
    if (dest != null) points.add((lat: dest.lat, lng: dest.lng));
    for (final p in trail) {
      points.add((lat: p.lat, lng: p.lng));
    }
    if (tech != null) points.add((lat: tech.lat, lng: tech.lng));

    if (points.length >= 2) {
      final lats = points.map((p) => p.lat);
      final lngs = points.map((p) => p.lng);
      final minLat = lats.reduce((a, b) => a < b ? a : b);
      final maxLat = lats.reduce((a, b) => a > b ? a : b);
      final minLng = lngs.reduce((a, b) => a < b ? a : b);
      final maxLng = lngs.reduce((a, b) => a > b ? a : b);
      final latSpan = (maxLat - minLat).abs().clamp(0.0001, 1.0);
      final lngSpan = (maxLng - minLng).abs().clamp(0.0001, 1.0);

      double normX(double lng) => ((lng - minLng) / lngSpan) * 2 - 1;
      double normY(double lat) => -(((lat - minLat) / latSpan) * 2 - 1);

      if (tech != null) {
        techAlign = Alignment(normX(tech.lng).clamp(-0.85, 0.85),
            normY(tech.lat).clamp(-0.85, 0.85));
      }
      if (dest != null) {
        destAlign = Alignment(normX(dest.lng).clamp(-0.85, 0.85),
            normY(dest.lat).clamp(-0.85, 0.85));
      }
      for (final p in trail) {
        trailAlignments.add(
          Alignment(
            normX(p.lng).clamp(-0.85, 0.85),
            normY(p.lat).clamp(-0.85, 0.85),
          ),
        );
      }
    }

    return Container(
      height: 200,
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
          for (final align in trailAlignments)
            Align(
              alignment: align,
              child: Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: AppColors.green,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          if (dest != null)
            Align(
              alignment: destAlign,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircleAvatar(
                    radius: 16,
                    backgroundColor: AppColors.ink700,
                    child: Icon(Icons.home_outlined,
                        color: Colors.white, size: 16),
                  ),
                  const SizedBox(height: 2),
                  Text(dest.label,
                      style: const TextStyle(
                          fontSize: 9,
                          fontWeight: FontWeight.w700,
                          color: AppColors.ink700)),
                ],
              ),
            ),
          Align(
            alignment: techAlign,
            child: const CircleAvatar(
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
          CircleAvatar(
            radius: 20,
            backgroundColor: AppColors.green,
            child: IconButton(
              padding: EdgeInsets.zero,
              icon: const Icon(Icons.call, color: Colors.white, size: 18),
              onPressed: tech.phone != null ? () {} : null,
            ),
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
