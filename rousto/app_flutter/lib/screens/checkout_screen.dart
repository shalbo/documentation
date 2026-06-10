import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../api/api_client.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';

class CheckoutScreen extends StatefulWidget {
  final double amountLyd;
  final String orderType;
  final String? orderId;
  final String? vendorId;

  const CheckoutScreen({
    super.key,
    required this.amountLyd,
    this.orderType = 'part_order',
    this.orderId,
    this.vendorId,
  });

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _api = ApiClient();
  bool _loading = true;
  String? _error;
  List<Map<String, dynamic>> _gateways = [];
  double _walletBalance = 0;
  String? _selectedGateway;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await _api.getLibyanCheckoutOptions();
      setState(() {
        _gateways = (data['gateways'] as List<dynamic>)
            .cast<Map<String, dynamic>>();
        _walletBalance = (data['wallet']?['balance_lyd'] as num?)?.toDouble() ?? 0;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  IconData _iconFor(String? icon) {
    switch (icon) {
      case 'cash':
        return Icons.payments_outlined;
      case 'wallet':
        return Icons.account_balance_wallet_outlined;
      case 'card':
        return Icons.credit_card;
      case 'mobile':
        return Icons.phone_android;
      default:
        return Icons.account_balance;
    }
  }

  Future<void> _pay() async {
    if (_selectedGateway == null) return;
    setState(() => _loading = true);
    try {
      final result = await _api.checkoutLibyan(
        amountLyd: widget.amountLyd,
        gateway: _selectedGateway!,
        orderType: widget.orderType,
        orderId: widget.orderId,
        vendorId: widget.vendorId,
      );
      final redirect = result['redirect_url'] as String?;
      if (redirect != null && (result['requires_webview'] == true)) {
        if (!mounted) return;
        final ok = await Navigator.of(context).push<bool>(
          MaterialPageRoute(
            builder: (_) => _PaymentWebView(url: redirect),
          ),
        );
        if (ok == true && mounted) {
          Navigator.of(context).pop(true);
        }
      } else if (mounted) {
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الدفع')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SoftCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('المبلغ الإجمالي',
                            style: TextStyle(color: AppColors.ink500, fontSize: 12)),
                        Text(
                          '${widget.amountLyd.toStringAsFixed(2)} د.ل',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                            color: AppColors.navy,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'رصيد المحفظة: ${_walletBalance.toStringAsFixed(2)} د.ل',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.ink500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'خيارات الدفع المحلية فقط',
                    style: TextStyle(
                      fontWeight: FontWeight.w800,
                      color: AppColors.navy,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Expanded(
                    child: ListView.separated(
                      itemCount: _gateways.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (_, i) {
                        final g = _gateways[i];
                        final slug = g['slug'] as String;
                        final selected = _selectedGateway == slug;
                        return Material(
                          color: selected ? AppColors.red050 : AppColors.surface,
                          borderRadius: BorderRadius.circular(14),
                          child: ListTile(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                              side: BorderSide(
                                color: selected ? AppColors.red : AppColors.line,
                              ),
                            ),
                            leading: Icon(
                              _iconFor(g['icon'] as String?),
                              color: AppColors.navy,
                            ),
                            title: Text(
                              g['name_ar'] as String,
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                                color: AppColors.navy,
                              ),
                            ),
                            trailing: selected
                                ? const Icon(Icons.check_circle, color: AppColors.red)
                                : null,
                            onTap: () => setState(() => _selectedGateway = slug),
                          ),
                        );
                      },
                    ),
                  ),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(_error!, style: const TextStyle(color: AppColors.red)),
                    ),
                  SizedBox(
                    height: 48,
                    child: ElevatedButton(
                      onPressed: _selectedGateway == null ? null : _pay,
                      child: const Text('تأكيد الدفع'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class _PaymentWebView extends StatefulWidget {
  final String url;
  const _PaymentWebView({required this.url});

  @override
  State<_PaymentWebView> createState() => _PaymentWebViewState();
}

class _PaymentWebViewState extends State<_PaymentWebView> {
  late final WebViewController _controller;
  bool _done = false;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (url) {
            if (url.contains('success') || url.contains('rousto://payment/return')) {
              if (!_done) {
                _done = true;
                Navigator.of(context).pop(true);
              }
            }
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('بوابة الدفع الآمنة')),
      body: WebViewWidget(controller: _controller),
    );
  }
}
