class Endpoints {
  // Auth
  static const String loginPhone = '/auth/login-phone';
  static const String sendOtp = '/auth/send-otp';
  static const String verifyOtp = '/auth/verify-otp';
  static const String loginEmail = '/auth/login';
  static const String loginGoogle = '/auth/google';
  static const String register = '/auth/register';
  static const String refresh = '/auth/refresh';
  static const String logout = '/auth/logout';
  static const String checkSession = '/auth/check-session';

  // User
  static const String me = '/auth/me';
  static String userById(String id) => '/users/$id';

  // Profile
  static const String scanFace = '/profile/scan-face';
  static const String saveProfile = '/profile/save-edits';
  static String profile(String customerId) => '/profile/$customerId';

  // Dashboard
  static const String dashboard = '/dashboard';
}
