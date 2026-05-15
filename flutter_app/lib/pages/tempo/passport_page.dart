import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';

class PassportPage extends StatelessWidget {
  const PassportPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 18),
          onPressed: () => context.pop(),
        ),
        title: const Text(
          'BEAUTY PASSPORT',
          style: TextStyle(
            color: Color(0xFFC9A96E),
            fontSize: 10,
            fontWeight: FontWeight.w700,
            letterSpacing: 2.0,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 20),
            // Digital Twin visualization
            Stack(
              alignment: Alignment.center,
              children: [
                Container(
                  width: 200,
                  height: 200,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFFC9A96E).withOpacity(0.2), width: 1),
                  ),
                ),
                Container(
                  width: 160,
                  height: 160,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFFC9A96E).withOpacity(0.4), width: 1),
                  ),
                ),
                Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      colors: [Color(0xFFE8D3A2), Color(0xFFC9A96E)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFC9A96E).withOpacity(0.4),
                        blurRadius: 40,
                      )
                    ],
                  ),
                  child: const Center(
                    child: Text(
                      '84',
                      style: TextStyle(
                        color: Color(0xFF0A0A0F),
                        fontSize: 42,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                Positioned(
                  top: 0,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0A0A0F),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFFC9A96E)),
                    ),
                    child: const Text(
                      'AI CONFIDENCE',
                      style: TextStyle(color: Color(0xFFC9A96E), fontSize: 8, fontWeight: FontWeight.bold, letterSpacing: 1.0),
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: 40),
            const Text(
              'Digital Twin Identity',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontFamily: 'Playfair Display',
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Updated 2 hours ago via Beautrix Scanner',
              style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12),
            ),
            const SizedBox(height: 40),
            
            // Stats grid
            Row(
              children: [
                Expanded(child: _buildStatCard('Skin Health', '92%')),
                const SizedBox(width: 16),
                Expanded(child: _buildStatCard('Hair Porosity', 'Medium')),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _buildStatCard('Undertone', 'Warm')),
                const SizedBox(width: 16),
                Expanded(child: _buildStatCard('Archetype', 'Bloom')),
              ],
            ),
            const SizedBox(height: 40),

            // Traits
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.03),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.white.withOpacity(0.08)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'AI TRAIT ANALYSIS',
                    style: TextStyle(
                      color: Color(0xFFC9A96E),
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildTraitBar('Hydration', 0.8),
                  const SizedBox(height: 12),
                  _buildTraitBar('Elasticity', 0.65),
                  const SizedBox(height: 12),
                  _buildTraitBar('Keratin Levels', 0.4),
                ],
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.02),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.0),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildTraitBar(String label, double fill) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500)),
            Text('${(fill * 100).toInt()}%', style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12)),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 6,
          width: double.infinity,
          decoration: BoxDecoration(color: Colors.white.withOpacity(0.1), borderRadius: BorderRadius.circular(3)),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: fill,
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFFC9A96E),
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
        )
      ],
    );
  }
}
