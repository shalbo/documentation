/// عملة التطبيق — دينار
const String kCurrencyLabel = 'دينار';

String formatAmount(num amount) => '${amount.round()} $kCurrencyLabel';

String formatAmountPerMonth(num amount) => '${amount.round()} $kCurrencyLabel/شهر';
