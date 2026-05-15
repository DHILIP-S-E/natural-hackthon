export type UserRole =
  | 'super_admin'
  | 'regional_manager'
  | 'franchise_owner'
  | 'salon_manager'
  | 'stylist'
  | 'customer';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  avatar_url?: string;
  phone?: string;
  preferred_language?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}
