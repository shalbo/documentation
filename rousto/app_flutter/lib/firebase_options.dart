// Run `flutterfire configure` to generate real options for your Firebase project.
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      default:
        throw UnsupportedError('FCM not configured for this platform.');
    }
  }

  // Placeholder — replace via flutterfire configure
  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'REPLACE_ME',
    appId: '1:000000000000:web:000000000000',
    messagingSenderId: '000000000000',
    projectId: 'rousto-app',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'REPLACE_ME',
    appId: '1:000000000000:android:000000000000',
    messagingSenderId: '000000000000',
    projectId: 'rousto-app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'REPLACE_ME',
    appId: '1:000000000000:ios:000000000000',
    messagingSenderId: '000000000000',
    projectId: 'rousto-app',
    iosBundleId: 'com.rousto.app',
  );
}
