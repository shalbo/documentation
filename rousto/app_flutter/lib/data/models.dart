import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

class ServiceItem {
  final String name;
  final String subtitle;
  final IconData icon;
  final int price;
  final String duration;

  const ServiceItem({
    required this.name,
    required this.subtitle,
    required this.icon,
    required this.price,
    required this.duration,
  });
}

class CategoryChip {
  final String label;
  const CategoryChip(this.label);
}

class TrackStep {
  final String title;
  final String time;
  final TrackStatus status;
  const TrackStep(this.title, this.time, this.status);
}

enum TrackStatus { done, current, todo }

class Testimonial {
  final String name;
  final String city;
  final String quote;
  const Testimonial(this.name, this.city, this.quote);
}

/// بيانات تجريبية للتطبيق.
class AppData {
  AppData._();

  static const List<CategoryChip> categories = [
    CategoryChip('الكل'),
    CategoryChip('زيت'),
    CategoryChip('إطارات'),
    CategoryChip('فرامل'),
    CategoryChip('تكييف'),
    CategoryChip('كهرباء'),
  ];

  static const List<ServiceItem> services = [
    ServiceItem(
      name: 'تغيير الزيت والفلاتر',
      subtitle: 'زيت أصلي + فحص شامل',
      icon: Icons.oil_barrel_outlined,
      price: 120,
      duration: '45 دقيقة',
    ),
    ServiceItem(
      name: 'الإطارات والترصيص',
      subtitle: 'موازنة وتبديل الإطارات',
      icon: Icons.tire_repair_outlined,
      price: 90,
      duration: '30 دقيقة',
    ),
    ServiceItem(
      name: 'نظام الفرامل',
      subtitle: 'فحص واستبدال الفحمات',
      icon: Icons.disc_full_outlined,
      price: 180,
      duration: '60 دقيقة',
    ),
    ServiceItem(
      name: 'تكييف وتبريد',
      subtitle: 'تعبئة فريون وصيانة',
      icon: Icons.ac_unit,
      price: 150,
      duration: '50 دقيقة',
    ),
    ServiceItem(
      name: 'البطارية والكهرباء',
      subtitle: 'فحص وتركيب بطاريات',
      icon: Icons.battery_charging_full_outlined,
      price: 110,
      duration: '40 دقيقة',
    ),
    ServiceItem(
      name: 'فحص كمبيوتر شامل',
      subtitle: 'تشخيص إلكتروني دقيق',
      icon: Icons.laptop_mac_outlined,
      price: 75,
      duration: '35 دقيقة',
    ),
  ];

  static const List<TrackStep> trackSteps = [
    TrackStep('تم تأكيد الحجز', '9:02 ص', TrackStatus.done),
    TrackStep('تم تعيين الفني', '9:05 ص', TrackStatus.done),
    TrackStep('الفني في الطريق إليك', 'الآن · 12 دقيقة', TrackStatus.current),
    TrackStep('تنفيذ الخدمة', 'قيد الانتظار', TrackStatus.todo),
    TrackStep('اكتمال الخدمة', 'قيد الانتظار', TrackStatus.todo),
  ];

  static Color statusColor(TrackStatus s) {
    switch (s) {
      case TrackStatus.done:
        return AppColors.green;
      case TrackStatus.current:
        return AppColors.red;
      case TrackStatus.todo:
        return AppColors.ink300;
    }
  }
}
