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

  // Beauty Passport & Recommendations (Track 3)
  static String beautyPassport(String customerId) =>
      '/agents/track3/passport/full?customer_id=$customerId';
  static String nextRecommendation(String customerId) =>
      '/agents/track3/recommendations/next-best?customer_id=$customerId';

  // Bookings
  static const String bookings = '/bookings';

  // Loyalty
  static const String loyalty = '/loyalty/me';

  // Chatbot
  static const String chatbot = '/chatbot/message';

  // Skin tone analysis
  static const String skinToneAnalyze = '/skin-tone/analyze';
}
