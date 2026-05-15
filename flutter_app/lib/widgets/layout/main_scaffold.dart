import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'bottom_nav.dart';

class MainScaffold extends StatelessWidget {
  final Widget child;

  const MainScaffold({super.key, required this.child});

  static const _routes = ['/dashboard', '/profile'];

  int _indexForLocation(String location) {
    final index = _routes.indexWhere((r) => location.startsWith(r));
    return index < 0 ? 0 : index;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    return Scaffold(
      body: child,
      bottomNavigationBar: BottomNav(currentIndex: _indexForLocation(location)),
    );
  }
}
