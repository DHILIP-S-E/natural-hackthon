import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/user_provider.dart';
import '../../repositories/auth_repository.dart';
import '../../widgets/common/app_button.dart';
import '../../widgets/common/app_text_field.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _nameController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final form = ref.watch(authFormProvider);
    final notifier = ref.read(authFormProvider.notifier);

    return Scaffold(
      appBar: AppBar(leading: const BackButton()),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Create account',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Get started for free',
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
                label: 'Full name',
                hint: 'John Doe',
                controller: _nameController,
              ),
              const SizedBox(height: 16),
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
                label: 'Create Account',
                isLoading: form.isLoading,
                onPressed: () => _register(context),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Already have an account? '),
                  TextButton(
                    onPressed: () => context.pop(),
                    child: const Text('Sign in'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _register(BuildContext context) async {
    final notifier = ref.read(authFormProvider.notifier);
    final form = ref.read(authFormProvider);
    notifier.setLoading(true);
    notifier.setError(null);
    try {
      final authRepo = ref.read(authRepositoryProvider);
      final name = _nameController.text.trim().split(' ');
      await authRepo.register(
        firstName: name.first,
        lastName: name.length > 1 ? name.sublist(1).join(' ') : '',
        email: form.email,
        password: form.password,
      );
      if (context.mounted) context.go('/dashboard');
    } catch (e) {
      notifier.setError(e.toString());
    } finally {
      notifier.setLoading(false);
    }
  }
}
