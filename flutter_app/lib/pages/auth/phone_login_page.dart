import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../core/auth/auth_service.dart';
import '../../repositories/auth_repository.dart';
import '../../widgets/common/app_button.dart';

class PhoneLoginPage extends ConsumerStatefulWidget {
  const PhoneLoginPage({super.key});

  @override
  ConsumerState<PhoneLoginPage> createState() => _PhoneLoginPageState();
}

class _PhoneLoginPageState extends ConsumerState<PhoneLoginPage>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.scaffoldBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.bgGradient),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Brand
                  Center(
                    child: Container(
                      width: 72,
                      height: 72,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: AppColors.primaryGradient,
                      ),
                      child: const Icon(Icons.spa_rounded,
                          color: Colors.white, size: 36),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'Welcome to Natural',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: const Color(0xFF1A1A2E),
                        ),
                  ),
                  const SizedBox(height: 28),

                  // Tabs
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.6),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: TabBar(
                      controller: _tabs,
                      labelColor: AppColors.primary,
                      unselectedLabelColor: Colors.grey,
                      indicator: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(10),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.primary.withOpacity(0.1),
                            blurRadius: 8,
                          )
                        ],
                      ),
                      tabs: const [
                        Tab(text: 'Mobile'),
                        Tab(text: 'Email'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  SizedBox(
                    height: 280,
                    child: TabBarView(
                      controller: _tabs,
                      children: const [
                        _PhoneOtpTab(),
                        _EmailTab(),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),
                  _Divider(),
                  const SizedBox(height: 16),
                  _GoogleSignInButton(),
                  const SizedBox(height: 16),
                  Center(
                    child: Text(
                      'By continuing, you agree to our Terms & Privacy Policy',
                      textAlign: TextAlign.center,
                      style:
                          TextStyle(fontSize: 11, color: Colors.grey.shade400),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ── Phone tab (direct login, no OTP) ─────────────────────────────────────────

class _PhoneOtpTab extends ConsumerStatefulWidget {
  const _PhoneOtpTab();

  @override
  ConsumerState<_PhoneOtpTab> createState() => _PhoneOtpTabState();
}

class _PhoneOtpTabState extends ConsumerState<_PhoneOtpTab> {
  final _phoneCtrl = TextEditingController();
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _phoneCtrl.dispose();
    super.dispose();
  }

  String get _fullPhone =>
      '+91${_phoneCtrl.text.trim().replaceAll(RegExp(r'\D'), '')}';

  bool get _phoneValid => _phoneCtrl.text.trim().length == 10;

  Future<void> _login(BuildContext context) async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final result = await ref
          .read(authRepositoryProvider)
          .loginPhone(phone: _fullPhone);
      if (!context.mounted) return;
      _navigate(context, result);
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_error != null) ...[
          _ErrorBox(_error!),
          const SizedBox(height: 12),
        ],
        _PhoneField(controller: _phoneCtrl, onChanged: (_) => setState(() {})),
        const SizedBox(height: 20),
        AppButton(
          label: 'Continue',
          isLoading: _isLoading,
          onPressed: _phoneValid ? () => _login(context) : null,
        ),
      ],
    );
  }
}

// ── Email tab ─────────────────────────────────────────────────────────────────

class _EmailTab extends ConsumerStatefulWidget {
  const _EmailTab();

  @override
  ConsumerState<_EmailTab> createState() => _EmailTabState();
}

class _EmailTabState extends ConsumerState<_EmailTab> {
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _isLoading = false;
  bool _showPass = false;
  String? _error;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  Future<void> _login(BuildContext context) async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final result = await ref.read(authRepositoryProvider).loginEmail(
            email: _emailCtrl.text.trim(),
            password: _passCtrl.text,
          );
      if (!context.mounted) return;
      _navigate(context, result);
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_error != null) ...[
          _ErrorBox(_error!),
          const SizedBox(height: 12),
        ],
        _InputBox(
          controller: _emailCtrl,
          hint: 'email@example.com',
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 12),
        _InputBox(
          controller: _passCtrl,
          hint: '••••••••',
          obscureText: !_showPass,
          suffix: IconButton(
            icon: Icon(_showPass ? Icons.visibility_off : Icons.visibility,
                size: 18, color: Colors.grey),
            onPressed: () => setState(() => _showPass = !_showPass),
          ),
        ),
        const SizedBox(height: 20),
        AppButton(
          label: 'Sign In',
          isLoading: _isLoading,
          onPressed: _emailCtrl.text.isNotEmpty && _passCtrl.text.isNotEmpty
              ? () => _login(context)
              : null,
        ),
      ],
    );
  }
}

// ── Google Sign-In ────────────────────────────────────────────────────────────

class _GoogleSignInButton extends ConsumerWidget {
  const _GoogleSignInButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: () => _googleLogin(context, ref),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE0E0E0)),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 8,
                offset: const Offset(0, 2))
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                  shape: BoxShape.circle, color: Color(0xFF4285F4)),
              child: const Center(
                child: Text('G',
                    style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12)),
              ),
            ),
            const SizedBox(width: 10),
            const Text('Continue with Google',
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1A1A2E))),
          ],
        ),
      ),
    );
  }

  Future<void> _googleLogin(BuildContext context, WidgetRef ref) async {
    try {
      final authService = ref.read(authServiceProvider);
      final account = await authService.signInWithGoogle();
      if (account == null) return;
      final auth = await account.authentication;
      final idToken = auth.idToken;
      if (idToken == null) throw Exception('Could not get Google token');
      final result =
          await ref.read(authRepositoryProvider).googleLogin(idToken: idToken);
      if (!context.mounted) return;
      _navigate(context, result);
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
        );
      }
    }
  }
}

// ── Shared helpers ────────────────────────────────────────────────────────────

void _navigate(BuildContext context, Map<String, dynamic> result) {
  if (result['is_new_customer'] == true || result['face_scan_required'] == true) {
    context.go('/face-scan');
  } else {
    context.go('/tempo');
  }
}

class _ErrorBox extends StatelessWidget {
  final String message;
  const _ErrorBox(this.message);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(message,
          style: TextStyle(
              color: Theme.of(context).colorScheme.onErrorContainer,
              fontSize: 13)),
    );
  }
}

class _PhoneField extends StatelessWidget {
  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  const _PhoneField({required this.controller, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.aiBubbleBorder),
      ),
      child: Row(
        children: [
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
            decoration: const BoxDecoration(
                border: Border(right: BorderSide(color: Color(0xFFEEE6FF)))),
            child: const Text('🇮🇳 +91',
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1A1A2E))),
          ),
          Expanded(
            child: TextField(
              controller: controller,
              keyboardType: TextInputType.phone,
              maxLength: 10,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              decoration: const InputDecoration(
                hintText: '9876543210',
                hintStyle: TextStyle(color: Color(0xFFB0A8C0)),
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(horizontal: 14),
                counterText: '',
              ),
              style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFF1A1A2E)),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }
}


class _InputBox extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final TextInputType? keyboardType;
  final bool obscureText;
  final Widget? suffix;
  const _InputBox({
    required this.controller,
    required this.hint,
    this.keyboardType,
    this.obscureText = false,
    this.suffix,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      decoration: InputDecoration(
        hintText: hint,
        filled: true,
        fillColor: Colors.white,
        suffixIcon: suffix,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: AppColors.aiBubbleBorder),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
    );
  }
}

class _Divider extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: Divider(color: Colors.grey.shade300)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text('or',
              style: TextStyle(color: Colors.grey.shade500, fontSize: 13)),
        ),
        Expanded(child: Divider(color: Colors.grey.shade300)),
      ],
    );
  }
}
