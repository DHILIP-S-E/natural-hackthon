import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/api/api_client.dart';
import '../../core/auth/auth_service.dart';
import '../../providers/user_provider.dart';
import '../../repositories/auth_repository.dart';
import '../../widgets/common/app_button.dart';
import '../../widgets/common/app_text_field.dart';

class LoginPage extends ConsumerWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final form = ref.watch(authFormProvider);
    final notifier = ref.read(authFormProvider.notifier);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Welcome back',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Sign in to your account',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                ),
                const SizedBox(height: 32),

                // Error banner
                if (form.error != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.errorContainer,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      form.error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onErrorContainer,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Email / password form
                AppTextField(
                  label: 'Email',
                  hint: 'you@example.com',
                  keyboardType: TextInputType.emailAddress,
                  onChanged: notifier.setEmail,
                ),
                const SizedBox(height: 16),
                AppTextField(
                  label: 'Password',
                  hint: '••••••••',
                  obscureText: true,
                  onChanged: notifier.setPassword,
                ),
                const SizedBox(height: 24),
                AppButton(
                  label: 'Sign In',
                  isLoading: form.isLoading,
                  onPressed: () => _login(context, ref),
                ),
                const SizedBox(height: 16),
                AppButton(
                  label: 'Continue with Google',
                  variant: AppButtonVariant.outlined,
                  onPressed: () => _googleLogin(context, ref),
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text("Don't have an account? "),
                    TextButton(
                      onPressed: () => context.push('/register'),
                      child: const Text('Register'),
                    ),
                  ],
                ),

                // ── Quick Demo Login ───────────────────────────────────────
                const SizedBox(height: 24),
                const Divider(),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.bolt_rounded,
                      size: 14,
                      color: Theme.of(context).colorScheme.outline,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Quick Demo Login — tap any role to sign in instantly',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: Theme.of(context).colorScheme.outline,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const _DemoLoginGrid(),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ── Normal email/password login ──────────────────────────────────────────
  Future<void> _login(BuildContext context, WidgetRef ref) async {
    final notifier = ref.read(authFormProvider.notifier);
    final form = ref.read(authFormProvider);
    notifier.setLoading(true);
    notifier.setError(null);
    try {
      await ref
          .read(authRepositoryProvider)
          .login(email: form.email, password: form.password);
      if (context.mounted) context.go('/dashboard');
    } catch (e) {
      notifier.setError(e.toString());
    } finally {
      notifier.setLoading(false);
    }
  }

  // ── Google Sign-In ───────────────────────────────────────────────────────
  Future<void> _googleLogin(BuildContext context, WidgetRef ref) async {
    final notifier = ref.read(authFormProvider.notifier);
    notifier.setLoading(true);
    notifier.setError(null);
    try {
      final authService = ref.read(authServiceProvider);
      final account = await authService.signInWithGoogle();
      if (account == null) return;
      final idToken = await authService.getGoogleIdToken();
      if (idToken == null) throw Exception('Could not get Google token');
      await ref.read(authRepositoryProvider).googleLogin(idToken: idToken);
      if (context.mounted) context.go('/dashboard');
    } catch (e) {
      notifier.setError(e.toString());
    } finally {
      notifier.setLoading(false);
    }
  }

}

// ── Demo credentials ─────────────────────────────────────────────────────────

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
      await ref.read(authRepositoryProvider).login(
            email: account.email,
            password: _password,
          );
      if (context.mounted) context.go('/dashboard');
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

// ── Demo Login Card ───────────────────────────────────────────────────────────
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
              : Theme.of(context).colorScheme.surface,
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
                style: TextStyle(
                  fontSize: 9,
                  color: Theme.of(context).colorScheme.outline,
                ),
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                '🔑 ${widget.demoPassword}',
                style: TextStyle(
                  fontSize: 9,
                  color: Theme.of(context).colorScheme.outline,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
