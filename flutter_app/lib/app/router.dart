import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../core/auth/auth_service.dart';
import '../pages/auth/phone_login_page.dart';
import '../pages/auth/login_page.dart';
import '../pages/auth/register_page.dart';
import '../pages/onboarding/face_scan_page.dart';
import '../pages/onboarding/profile_review_page.dart';
import '../pages/tempo/home_page.dart';
import '../pages/auth/signup_page.dart';
import '../pages/tempo/chat_page.dart';
import '../pages/tempo/voice_page.dart';
import '../pages/tempo/bookings_page.dart';
import '../pages/tempo/beauty_pass_page.dart';
import '../pages/tempo/passport_page.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authService = ref.watch(authServiceProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) async {
      final isAuthenticated = await authService.isAuthenticated();
      final loc = state.matchedLocation;
      final onPublicPage = loc == '/login' ||
          loc == '/register' ||
          loc == '/phone-login';
      if (!isAuthenticated && !onPublicPage) return '/phone-login';
      if (isAuthenticated && onPublicPage) return '/tempo';
      return null;
    },
    routes: [
      GoRoute(
        path: '/phone-login',
        pageBuilder: (context, state) => _slide(state, const PhoneLoginPage()),
      ),
      GoRoute(
        path: '/login',
        redirect: (_, __) => '/phone-login',
        routes: const [],
      ),
      GoRoute(
        path: '/register',
        pageBuilder: (context, state) => _slide(state, const RegisterPage()),
      ),
      GoRoute(
        path: '/signup',
        pageBuilder: (context, state) => _slide(state, const SignupPage()),
      ),
      GoRoute(
        path: '/face-scan',
        pageBuilder: (context, state) => _slide(state, const FaceScanPage()),
      ),
      GoRoute(
        path: '/profile-review',
        pageBuilder: (context, state) =>
            _slide(state, const ProfileReviewPage()),
      ),
      GoRoute(
        path: '/tempo',
        pageBuilder: (context, state) => _slide(state, const TempoHomePage()),
      ),
      GoRoute(
        path: '/tempo/chat',
        pageBuilder: (context, state) {
          final initial = state.extra as String?;
          return _slide(state, TempoChatPage(initialText: initial));
        },
      ),
      GoRoute(
        path: '/tempo/voice',
        pageBuilder: (context, state) =>
            _slide(state, const TempoVoicePage()),
      GoRoute(
        path: '/tempo/bookings',
        pageBuilder: (context, state) =>
            _slide(state, const BookingsPage()),
      ),
      GoRoute(
        path: '/tempo/pass',
        pageBuilder: (context, state) =>
            _slide(state, const BeautyPassPage()),
      ),
      GoRoute(
        path: '/tempo/passport',
        pageBuilder: (context, state) =>
            _slide(state, const PassportPage()),
      ),
    ],
  );
});

CustomTransitionPage<void> _slide<T>(GoRouterState state, Widget child) {
  return CustomTransitionPage<void>(
    key: state.pageKey,
    child: child,
    transitionDuration: const Duration(milliseconds: 280),
    reverseTransitionDuration: const Duration(milliseconds: 220),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      final slide = Tween<Offset>(
        begin: const Offset(0.05, 0),
        end: Offset.zero,
      ).animate(CurvedAnimation(parent: animation, curve: Curves.easeOut));

      return SlideTransition(
        position: slide,
        child: FadeTransition(opacity: animation, child: child),
      );
    },
  );
}
