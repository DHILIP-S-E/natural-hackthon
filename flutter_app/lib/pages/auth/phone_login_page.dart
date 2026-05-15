import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../core/api/api_client.dart';
import '../../core/auth/auth_service.dart';
import '../../repositories/auth_repository.dart';
import '../../widgets/common/app_button.dart';

class PhoneLoginPage extends ConsumerWidget {
  const PhoneLoginPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
                  const SizedBox(height: 8),
                  Text(
                    'Sign in to your account',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
                  ),
                  const SizedBox(height: 36),
                  const _EmailTab(),
                  const SizedBox(height: 20),
                  _Divider(),
                  const SizedBox(height: 20),
                  const _GoogleSignInButton(),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        "Don't have an account? ",
                        style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
                      ),
                      GestureDetector(
                        onTap: () => context.push('/signup'),
                        child: const Text(
                          'Sign up',
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
                  const _Divider(text: 'Quick Demo Login'),
                  const SizedBox(height: 16),
                  const _DemoLoginGrid(),
                  const SizedBox(height: 24),
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
  final String text;
  const _Divider({this.text = 'or'});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: Divider(color: Colors.grey.shade300)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(text,
              style: TextStyle(color: Colors.grey.shade500, fontSize: 13)),
        ),
        Expanded(child: Divider(color: Colors.grey.shade300)),
      ],
    );
  }
}

// ── Demo credentials & Grid ───────────────────────────────────────────────────

class _DemoAccount {
  final String email;
  final String label;
  final String icon;
  final Color color;

  const _DemoAccount({
    required this.email,
    required this.label,
    required this.icon,
    required this.color,
  });
}

class _DemoLoginGrid extends ConsumerStatefulWidget {
  const _DemoLoginGrid();

  @override
  ConsumerState<_DemoLoginGrid> createState() => _DemoLoginGridState();
}

class _DemoLoginGridState extends ConsumerState<_DemoLoginGrid> {
  bool _isLoading = false;
  bool _fetchingAccounts = true;
  List<_DemoAccount> _accounts = [];
  String _password = '';

  @override
  void initState() {
    super.initState();
    _fetchDemoAccounts();
  }

  Future<void> _fetchDemoAccounts() async {
    try {
      // Need to import apiClientProvider if not already imported
      // Actually we have authRepositoryProvider which uses apiClient
      // We can use the ApiClient directly.
      final client = ref.read(apiClientProvider);
      final response = await client.get<Map<String, dynamic>>('/auth/demo-credentials');
      final data = response.data!['data'];
      final accountsList = data['accounts'] as List;
      
      if (mounted) {
        setState(() {
          _password = data['password'] as String;
          _accounts = accountsList.map((acc) {
            final colorHex = acc['color'].toString().replaceFirst('#', 'FF');
            return _DemoAccount(
              email: acc['email'],
              label: acc['label'],
              icon: acc['icon'],
              color: Color(int.parse(colorHex, radix: 16)),
            );
          }).toList();
          _fetchingAccounts = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _fetchingAccounts = false);
      }
    }
  }

  Future<void> _quickLogin(BuildContext context, _DemoAccount account) async {
    setState(() => _isLoading = true);
    try {
      final result = await ref.read(authRepositoryProvider).loginEmail(
            email: account.email,
            password: _password,
          );
      if (!context.mounted) return;
      _navigate(context, result);
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_fetchingAccounts) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }
    
    if (_accounts.isEmpty) return const SizedBox.shrink();

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      childAspectRatio: 2.2,
      children: _accounts.map((account) {
        return _DemoLoginCard(
          account: account,
          demoPassword: _password,
          isLoading: _isLoading,
          onTap: () => _quickLogin(context, account),
        );
      }).toList(),
    );
  }
}

class _DemoLoginCard extends StatefulWidget {
  final _DemoAccount account;
  final String demoPassword;
  final bool isLoading;
  final VoidCallback onTap;

  const _DemoLoginCard({
    required this.account,
    required this.demoPassword,
    required this.isLoading,
    required this.onTap,
  });

  @override
  State<_DemoLoginCard> createState() => _DemoLoginCardState();
}

class _DemoLoginCardState extends State<_DemoLoginCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final acc = widget.account;
    return GestureDetector(
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      onTap: widget.isLoading ? null : widget.onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: _pressed
              ? acc.color.withOpacity(0.08)
              : Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: _pressed ? acc.color : acc.color.withOpacity(0.30),
            width: 1.5,
          ),
          boxShadow: _pressed
              ? [
                  BoxShadow(
                    color: acc.color.withOpacity(0.20),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ]
              : [],
        ),
        child: Opacity(
          opacity: widget.isLoading ? 0.5 : 1.0,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                children: [
                  Text(acc.icon, style: const TextStyle(fontSize: 13)),
                  const SizedBox(width: 5),
                  Flexible(
                    child: Text(
                      acc.label,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: acc.color,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 3),
              Text(
                '📧 ${acc.email}',
                style: const TextStyle(
                  fontSize: 9,
                  color: Colors.grey,
                ),
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                '🔑 ${widget.demoPassword}',
                style: const TextStyle(
                  fontSize: 9,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
