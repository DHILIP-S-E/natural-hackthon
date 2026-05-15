import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
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
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _login(BuildContext context, WidgetRef ref) async {
    final notifier = ref.read(authFormProvider.notifier);
    final form = ref.read(authFormProvider);
    notifier.setLoading(true);
    notifier.setError(null);
    try {
      final authRepo = ref.read(authRepositoryProvider);
      await authRepo.login(email: form.email, password: form.password);
      if (context.mounted) context.go('/dashboard');
    } catch (e) {
      notifier.setError(e.toString());
    } finally {
      notifier.setLoading(false);
    }
  }

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
      final authRepo = ref.read(authRepositoryProvider);
      await authRepo.googleLogin(idToken: idToken);
      if (context.mounted) context.go('/dashboard');
    } catch (e) {
      notifier.setError(e.toString());
    } finally {
      notifier.setLoading(false);
    }
  }
}
