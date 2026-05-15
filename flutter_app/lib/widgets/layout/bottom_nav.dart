import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class BottomNav extends StatelessWidget {
  final int currentIndex;

  const BottomNav({super.key, required this.currentIndex});

  static const _destinations = [
    (icon: Icons.dashboard_outlined, activeIcon: Icons.dashboard, label: 'Dashboard', route: '/dashboard'),
    (icon: Icons.person_outline, activeIcon: Icons.person, label: 'Profile', route: '/profile'),
  ];

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: (index) {
        context.go(_destinations[index].route);
      },
      destinations: _destinations.map((d) {
        return NavigationDestination(
          icon: Icon(d.icon),
          selectedIcon: Icon(d.activeIcon),
          label: d.label,
        );
      }).toList(),
    );
  }
}
