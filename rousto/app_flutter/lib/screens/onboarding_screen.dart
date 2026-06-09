import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'root_nav.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  void _start(BuildContext context) {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const RootNav()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF000000), Color(0xFF0B2C44), Color(0xFF000000)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Stack(
          children: [
            // وهج أحمر زخرفي
            Positioned(
              top: -120,
              right: -100,
              child: Container(
                width: 340,
                height: 340,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: AppColors.redGradient,
                ),
              ),
            ),
            Positioned.fill(
              child: SafeArea(
                child: Column(
                  children: [
                    const Spacer(),
                    SvgPicture.asset('assets/logo.svg', height: 150),
                    const Spacer(),
                    Padding(
                      padding: const EdgeInsets.all(28),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              _dot(true),
                              _dot(false),
                              _dot(false),
                            ],
                          ),
                          const SizedBox(height: 18),
                          const Text(
                            'عناية ذكية بسيارتك',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 26,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'احجز خدمة الصيانة في ثوانٍ وتابعها مباشرةً من هاتفك مع فنيّين معتمدين.',
                            style: TextStyle(
                                color: Color(0xFFC7C8CF), height: 1.6),
                          ),
                          const SizedBox(height: 24),
                          GradientButton(
                            label: 'ابدأ الآن',
                            icon: Icons.arrow_back,
                            onPressed: () => _start(context),
                          ),
                          const SizedBox(height: 14),
                          Center(
                            child: GestureDetector(
                              onTap: () => _start(context),
                              child: const Text.rich(
                                TextSpan(
                                  text: 'لديك حساب؟ ',
                                  style: TextStyle(color: Color(0xFFC7C8CF)),
                                  children: [
                                    TextSpan(
                                      text: 'تسجيل الدخول',
                                      style: TextStyle(
                                        color: AppColors.red,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _dot(bool active) => AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        margin: const EdgeInsets.only(left: 6),
        width: active ? 22 : 8,
        height: 8,
        decoration: BoxDecoration(
          color: active ? AppColors.red : Colors.white24,
          borderRadius: BorderRadius.circular(999),
        ),
      );
}
