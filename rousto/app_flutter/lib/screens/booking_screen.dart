import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/app_repository.dart';
import '../data/models.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';

class BookingScreen extends StatefulWidget {
  final ServiceModel? service;
  const BookingScreen({super.key, this.service});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  final _repository = AppRepository();
  static const _slots = ['السبت', 'الأحد 9 ص', 'الاثنين', 'الثلاثاء'];

  bool _loading = true;
  int _slot = 1;
  double _discount = 30;
  double _total = 0;

  VehicleModel? _vehicle;
  AddressModel? _address;
  PaymentMethodModel? _payment;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final service = widget.service;
    final price = service?.priceSar ?? 120.0;
    final contextData = await _repository.loadBookingContext();
    final promo = await _repository.validatePromo('ROUSTO', price);
    setState(() {
      _vehicle = contextData.vehicle;
      _address = contextData.address;
      _payment = contextData.payment;
      _discount = promo.discount;
      _total = promo.total;
      _loading = false;
    });
  }

  ServiceModel get _service {
    if (widget.service != null) return widget.service!;
    final state = context.read<AppState>();
    if (state.currentServices.isNotEmpty) return state.currentServices.first;
    if (state.categories.isNotEmpty && state.categories.first.services.isNotEmpty) {
      return state.categories.first.services.first;
    }
    throw StateError('لا توجد خدمات متاحة');
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final s = _service;
    final vehicle = _vehicle!;
    final address = _address!;
    final payment = _payment!;

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
            _InfoRow(
              icon: Icons.directions_car_filled_outlined,
              title: vehicle.displayTitle,
              subtitle: vehicle.displaySubtitle,
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
            _InfoRow(
              icon: Icons.location_on_outlined,
              title: address.label,
              subtitle: address.displaySubtitle,
            ),
            const SizedBox(height: 18),
            const _Label('طريقة الدفع'),
            _InfoRow(
              icon: Icons.credit_card,
              title: payment.labelAr,
              subtitle: 'بطاقة افتراضية',
            ),
            const SizedBox(height: 18),
            SoftCard(
              child: Column(
                children: [
                  _summaryRow('الخدمة', '${s.price} ريال'),
                  const SizedBox(height: 6),
                  _summaryRow('خصم (ROUSTO)', '- ${_discount.round()} ريال',
                      color: AppColors.green),
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8),
                    child: Divider(color: AppColors.line, height: 1),
                  ),
                  _summaryRow('الإجمالي', '${_total.round()} ريال',
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
          label: 'تأكيد ودفع ${_total.round()} ريال',
          onPressed: () => _confirm(context, s, vehicle, address, payment),
        ),
      ),
    );
  }

  Future<void> _confirm(
    BuildContext context,
    ServiceModel service,
    VehicleModel vehicle,
    AddressModel address,
    PaymentMethodModel payment,
  ) async {
    final ok = await _repository.createBooking(
      serviceId: service.id,
      vehicleId: vehicle.id,
      addressId: address.id,
      paymentMethodId: payment.id,
      promotionCode: 'ROUSTO',
    );

    if (!context.mounted) return;

    await context.read<AppState>().refreshActiveBooking();

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
            Text(
              ok ? 'تم تأكيد حجزك!' : 'تم حفظ الحجز محلياً',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 6),
            Text(
              ok
                  ? 'سيتواصل معك فريق روستو لتأكيد التفاصيل.'
                  : 'تعذّر الاتصال بالخادم — تم الحفظ في الوضع التجريبي.',
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppColors.ink500),
            ),
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
