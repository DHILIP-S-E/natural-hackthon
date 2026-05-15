import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../repositories/auth_repository.dart';
import '../../widgets/common/app_button.dart';

class SignupPage extends ConsumerStatefulWidget {
  const SignupPage({super.key});

  @override
  ConsumerState<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends ConsumerState<SignupPage> {
  final _firstNameCtrl = TextEditingController();
  final _lastNameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();

  bool _showPass = false;
  bool _showConfirm = false;
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _passCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  bool get _valid =>
      _firstNameCtrl.text.trim().isNotEmpty &&
      _lastNameCtrl.text.trim().isNotEmpty &&
      _emailCtrl.text.trim().isNotEmpty &&
      _passCtrl.text.length >= 6 &&
      _passCtrl.text == _confirmCtrl.text;

  Future<void> _signup() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      await ref.read(authRepositoryProvider).register(
            firstName: _firstNameCtrl.text.trim(),
            lastName: _lastNameCtrl.text.trim(),
            email: _emailCtrl.text.trim(),
            password: _passCtrl.text,
            phone: _phoneCtrl.text.trim().isEmpty
                ? null
                : '+91${_phoneCtrl.text.trim()}',
          );
      if (!mounted) return;
      context.go('/face-scan');
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.scaffoldBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.bgGradient),
        child: SafeArea(
          child: Column(
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: IconButton(
                  onPressed: () => context.pop(),
                  icon: const Icon(Icons.arrow_back_ios_new_rounded,
                      color: Color(0xFF1A1A2E), size: 20),
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 28),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 4),
                      Center(
                        child: Container(
                          width: 64,
                          height: 64,
                          decoration: const BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: AppColors.primaryGradient,
                          ),
                          child: const Icon(Icons.spa_rounded,
                              color: Colors.white, size: 30),
                        ),
                      ),
                      const SizedBox(height: 14),
                      const Text(
                        'Create account',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF1A1A2E)),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Join Natural — your beauty journey starts here',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            fontSize: 13, color: Colors.grey.shade500),
                      ),
                      const SizedBox(height: 24),

                      if (_error != null) ...[
                        _ErrorBox(_error!),
                        const SizedBox(height: 14),
                      ],

                      // First + Last name row
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _label('First name'),
                                const SizedBox(height: 6),
                                _Field(
                                  controller: _firstNameCtrl,
                                  hint: 'Dhilip',
                                  onChanged: (_) => setState(() {}),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _label('Last name'),
                                const SizedBox(height: 6),
                                _Field(
                                  controller: _lastNameCtrl,
                                  hint: 'Kumar',
                                  onChanged: (_) => setState(() {}),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),

                      _label('Email'),
                      const SizedBox(height: 6),
                      _Field(
                        controller: _emailCtrl,
                        hint: 'you@example.com',
                        keyboardType: TextInputType.emailAddress,
                        onChanged: (_) => setState(() {}),
                      ),
                      const SizedBox(height: 14),

                      _label('Phone (optional)'),
                      const SizedBox(height: 6),
                      _PhoneField(controller: _phoneCtrl),
                      const SizedBox(height: 14),

                      _label('Password'),
                      const SizedBox(height: 6),
                      _Field(
                        controller: _passCtrl,
                        hint: 'Min. 6 characters',
                        obscureText: !_showPass,
                        onChanged: (_) => setState(() {}),
                        suffix: _eyeBtn(
                          visible: _showPass,
                          onTap: () =>
                              setState(() => _showPass = !_showPass),
                        ),
                      ),
                      const SizedBox(height: 14),

                      _label('Confirm password'),
                      const SizedBox(height: 6),
                      _Field(
                        controller: _confirmCtrl,
                        hint: '••••••••',
                        obscureText: !_showConfirm,
                        onChanged: (_) => setState(() {}),
                        suffix: _eyeBtn(
                          visible: _showConfirm,
                          onTap: () =>
                              setState(() => _showConfirm = !_showConfirm),
                        ),
                      ),

                      if (_confirmCtrl.text.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        _MatchRow(match: _passCtrl.text == _confirmCtrl.text),
                      ],

                      const SizedBox(height: 26),
                      AppButton(
                        label: 'Create Account',
                        isLoading: _isLoading,
                        onPressed: _valid ? _signup : null,
                      ),
                      const SizedBox(height: 18),

                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Already have an account? ',
                            style: TextStyle(
                                fontSize: 13, color: Colors.grey.shade500),
                          ),
                          GestureDetector(
                            onTap: () => context.pop(),
                            child: const Text(
                              'Sign in',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: AppColors.primary,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _label(String text) => Text(
        text,
        style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Color(0xFF1A1A2E)),
      );

  Widget _eyeBtn({required bool visible, required VoidCallback onTap}) =>
      IconButton(
        icon: Icon(visible ? Icons.visibility_off : Icons.visibility,
            size: 18, color: Colors.grey),
        onPressed: onTap,
      );
}

// ── Shared widgets ────────────────────────────────────────────────────────────

class _ErrorBox extends StatelessWidget {
  final String message;
  const _ErrorBox(this.message);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFFFEBEE),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(message,
          style:
              const TextStyle(color: Color(0xFFB00020), fontSize: 13)),
    );
  }
}

class _MatchRow extends StatelessWidget {
  final bool match;
  const _MatchRow({required this.match});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          match ? Icons.check_circle_rounded : Icons.cancel_rounded,
          size: 14,
          color: match ? Colors.green : Colors.red,
        ),
        const SizedBox(width: 6),
        Text(
          match ? 'Passwords match' : 'Passwords do not match',
          style: TextStyle(
              fontSize: 12, color: match ? Colors.green : Colors.red),
        ),
      ],
    );
  }
}

class _PhoneField extends StatelessWidget {
  final TextEditingController controller;
  const _PhoneField({required this.controller});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFEEE6FF)),
      ),
      child: Row(
        children: [
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
            decoration: const BoxDecoration(
              border: Border(
                  right: BorderSide(color: Color(0xFFEEE6FF))),
            ),
            child: const Text('🇮🇳 +91',
                style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1A1A2E))),
          ),
          Expanded(
            child: TextField(
              controller: controller,
              keyboardType: TextInputType.phone,
              maxLength: 10,
              decoration: const InputDecoration(
                hintText: '9876543210 (optional)',
                hintStyle: TextStyle(color: Color(0xFFB0A8C0), fontSize: 13),
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(horizontal: 12),
                counterText: '',
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Field extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final TextInputType? keyboardType;
  final bool obscureText;
  final Widget? suffix;
  final ValueChanged<String>? onChanged;

  const _Field({
    required this.controller,
    required this.hint,
    this.keyboardType,
    this.obscureText = false,
    this.suffix,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      onChanged: onChanged,
      style: const TextStyle(fontSize: 14, color: Color(0xFF1A1A2E)),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Color(0xFFB0A8C0), fontSize: 13),
        filled: true,
        fillColor: Colors.white,
        suffixIcon: suffix,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFEEE6FF)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFEEE6FF)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
    );
  }
}
