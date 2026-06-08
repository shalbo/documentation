import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../data/models.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'booking_screen.dart';
import 'tracking_screen.dart';

class HomeScreen extends StatefulWidget {
  final VoidCallback onBook;
  const HomeScreen({super.key, required this.onBook});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _category = 0;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.only(bottom: 110),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _header(context),
          Transform.translate(
            offset: const Offset(0, -16),
            child: _activeServiceCard(context),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 4, 18, 0),
            child: _categories(),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 0),
            child: RowHeader('الخدمات الشائعة', action: 'عرض الكل'),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
            child: _servicesGrid(context),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 0),
            child: _promo(),
          ),
        ],
      ),
    );
  }

  Widget _header(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 0, 18, 30),
      decoration: const BoxDecoration(
        gradient: AppColors.redGradient,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
      ),
      child: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    SvgPicture.asset('assets/logo.svg', height: 28),
                    const SizedBox(width: 8),
                    const Text('روستو',
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w800,
                            fontSize: 18)),
                  ],
                ),
                const CircleAvatar(
                  radius: 19,
                  backgroundColor: Colors.white24,
                  child: Text('س',
                      style: TextStyle(
                          color: Colors.white, fontWeight: FontWeight.w800)),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text('أهلاً بعودتك 👋',
                style: TextStyle(color: Color(0xFFFFD9DA), fontSize: 13)),
            const Text('سعود العتيبي',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w800)),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Row(
                children: [
                  Icon(Icons.search, color: Colors.white, size: 20),
                  SizedBox(width: 8),
                  Text('ابحث عن خدمة…',
                      style: TextStyle(color: Color(0xFFFFE1E1))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _activeServiceCard(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18),
      child: GestureDetector(
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => const TrackingScreen()),
        ),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.ink900,
            borderRadius: BorderRadius.circular(18),
          ),
          child: Row(
            children: [
              const IconBadge(Icons.build_outlined,
                  bg: AppColors.red, fg: Colors.white),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('خدمة جارية',
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w800)),
                    Text('تغيير الزيت · الفني في الطريق',
                        style:
                            TextStyle(color: Color(0xFFC7C8CF), fontSize: 12)),
                  ],
                ),
              ),
              const CircleAvatar(
                radius: 15,
                backgroundColor: Colors.white,
                child: Icon(Icons.arrow_back,
                    size: 16, color: AppColors.ink900),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _categories() {
    return SizedBox(
      height: 38,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: AppData.categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          final active = i == _category;
          return GestureDetector(
            onTap: () => setState(() => _category = i),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: active ? AppColors.red050 : AppColors.surface,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(
                    color: active ? Colors.transparent : AppColors.line),
              ),
              child: Text(
                AppData.categories[i].label,
                style: TextStyle(
                  color: active ? AppColors.red600 : AppColors.ink700,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _servicesGrid(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: AppData.services.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.25,
      ),
      itemBuilder: (_, i) {
        final s = AppData.services[i];
        return GestureDetector(
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => BookingScreen(service: s)),
          ),
          child: SoftCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IconBadge(s.icon, size: 40),
                const Spacer(),
                Text(s.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 14)),
                Text(s.duration,
                    style: const TextStyle(
                        color: AppColors.ink300, fontSize: 11)),
                const SizedBox(height: 4),
                Text('${s.price} ريال',
                    style: const TextStyle(
                        color: AppColors.red600,
                        fontWeight: FontWeight.w800,
                        fontSize: 13)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _promo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppColors.darkGradient,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('خصم على أول حجز',
                    style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 15)),
                Text('استخدم كود ROUSTO',
                    style:
                        TextStyle(color: Color(0xFFC7C8CF), fontSize: 12)),
              ],
            ),
          ),
          const Text('٢٥٪',
              style: TextStyle(
                  color: AppColors.red,
                  fontSize: 30,
                  fontWeight: FontWeight.w800)),
        ],
      ),
    );
  }
}
