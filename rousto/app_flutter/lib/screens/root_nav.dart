import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import 'booking_screen.dart';
import 'home_screen.dart';
import 'offers_screen.dart';
import 'profile_screen.dart';
import 'tracking_screen.dart';

class RootNav extends StatefulWidget {
  const RootNav({super.key});

  @override
  State<RootNav> createState() => _RootNavState();
}

class _RootNavState extends State<RootNav> {
  int _index = 0;

  late final List<Widget> _pages = [
    HomeScreen(onBook: _openBooking),
    const TrackingScreen(),
    const OffersScreen(),
    const ProfileScreen(),
  ];

  void _openBooking() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const BookingScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: IndexedStack(index: _index, children: _pages),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: AppColors.red.withValues(alpha: 0.4),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: FloatingActionButton(
          onPressed: _openBooking,
          backgroundColor: AppColors.red,
          elevation: 0,
          shape: const CircleBorder(),
          child: const Icon(Icons.add, color: Colors.white, size: 30),
        ),
      ),
      bottomNavigationBar: BottomAppBar(
        color: AppColors.surface,
        shape: const CircularNotchedRectangle(),
        notchMargin: 8,
        height: 70,
        padding: EdgeInsets.zero,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _tab(0, Icons.home_filled, 'الرئيسية'),
            _tab(1, Icons.receipt_long_outlined, 'طلباتي'),
            const SizedBox(width: 48),
            _tab(2, Icons.card_giftcard_outlined, 'عروض'),
            _tab(3, Icons.person_outline, 'حسابي'),
          ],
        ),
      ),
    );
  }

  Widget _tab(int i, IconData icon, String label) {
    final active = _index == i;
    final color = active ? AppColors.red600 : AppColors.ink300;
    return InkWell(
      onTap: () => setState(() => _index = i),
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 3),
            Text(label,
                style: TextStyle(
                    color: color,
                    fontSize: 11,
                    fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }
}
