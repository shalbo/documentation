import 'package:flutter/material.dart';

import '../api/api_client.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final _api = ApiClient();
  bool _loading = true;
  String? _error;
  int _unread = 0;
  List<Map<String, dynamic>> _items = [];
  List<Map<String, dynamic>> _prefs = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final notifs = await _api.getNotifications();
      final count = await _api.getNotificationUnreadCount();
      final prefs = await _api.getNotificationPreferences();
      if (!mounted) return;
      setState(() {
        _items = notifs;
        _unread = count;
        _prefs = prefs;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _markRead(String id) async {
    await _api.markNotificationRead(id);
    await _load();
  }

  Future<void> _markAllRead() async {
    await _api.markAllNotificationsRead();
    await _load();
  }

  Future<void> _savePrefs() async {
    await _api.updateNotificationPreferences(_prefs);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم حفظ التفضيلات')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text('الإشعارات',
            style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          if (_unread > 0)
            TextButton(
              onPressed: _markAllRead,
              child: const Text('قراءة الكل'),
            ),
          IconButton(onPressed: _load, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : ListView(
                  padding: const EdgeInsets.fromLTRB(18, 8, 18, 110),
                  children: [
                    if (_unread > 0)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Chip(
                          label: Text('$_unread غير مقروء'),
                          backgroundColor: AppColors.red050,
                        ),
                      ),
                    if (_items.isEmpty)
                      const SoftCard(
                        child: Padding(
                          padding: EdgeInsets.all(16),
                          child: Text('لا توجد إشعارات',
                              textAlign: TextAlign.center),
                        ),
                      )
                    else
                      ..._items.map(_notifCard),
                    const SizedBox(height: 20),
                    const Text('تفضيلات الإشعارات',
                        style: TextStyle(
                            fontWeight: FontWeight.w800, fontSize: 16)),
                    const SizedBox(height: 10),
                    SoftCard(
                      child: Column(
                        children: [
                          for (var i = 0; i < _prefs.length; i++) ...[
                            if (i > 0) const Divider(height: 1),
                            _prefRow(i),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _savePrefs,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.red,
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('حفظ التفضيلات'),
                      ),
                    ),
                  ],
                ),
    );
  }

  Widget _notifCard(Map<String, dynamic> n) {
    final isRead = n['is_read'] == true;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SoftCard(
        child: InkWell(
          onTap: isRead ? null : () => _markRead(n['id'] as String),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        n['title'] as String? ?? '',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 14,
                          color: isRead ? AppColors.ink500 : AppColors.ink900,
                        ),
                      ),
                    ),
                    if (!isRead)
                      Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: AppColors.red,
                          shape: BoxShape.circle,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  n['body'] as String? ?? '',
                  style: const TextStyle(
                      color: AppColors.ink500, fontSize: 13, height: 1.5),
                ),
                const SizedBox(height: 8),
                Text(
                  n['category_label_ar'] as String? ?? '',
                  style: const TextStyle(
                      color: AppColors.ink300, fontSize: 11),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _prefRow(int index) {
    final p = _prefs[index];
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(p['category_label_ar'] as String? ?? '',
              style: const TextStyle(fontWeight: FontWeight.w700)),
          Row(
            children: [
              Expanded(
                child: SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('داخل التطبيق', style: TextStyle(fontSize: 13)),
                  value: p['in_app_enabled'] == true,
                  onChanged: (v) => setState(() => _prefs[index]['in_app_enabled'] = v),
                ),
              ),
              Expanded(
                child: SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Push', style: TextStyle(fontSize: 13)),
                  value: p['push_enabled'] == true,
                  onChanged: (v) => setState(() => _prefs[index]['push_enabled'] = v),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
